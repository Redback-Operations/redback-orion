import gradio as gr
import argparse
import os
import sys
import tempfile
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, BitsAndBytesConfig, CLIPImageProcessor
from PIL import Image
import threading
import time

from model.LISA import LISAForCausalLM
from model.llava import conversation as conversation_lib
from model.llava.mm_utils import tokenizer_image_token
from model.segment_anything.utils.transforms import ResizeLongestSide
from utils.utils import (DEFAULT_IM_END_TOKEN, DEFAULT_IM_START_TOKEN,
                         DEFAULT_IMAGE_TOKEN, IMAGE_TOKEN_INDEX)

class LISASegmentor:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.clip_image_processor = None
        self.transform = None
        self.args = None
        
    def initialize_model(self, 
                        version="xinlai/LISA-13B-llama2-v1",
                        precision="fp16",
                        image_size=1024,
                        model_max_length=512,
                        vision_tower="openai/clip-vit-large-patch14",
                        conv_type="llava_v1",
                        load_in_4bit=False,
                        load_in_8bit=True):
        """Initialize the LISA model"""
        
        # Create args object
        self.args = argparse.Namespace()
        self.args.version = version
        self.args.precision = precision
        self.args.image_size = image_size
        self.args.model_max_length = model_max_length
        self.args.vision_tower = vision_tower
        self.args.conv_type = conv_type
        self.args.load_in_4bit = load_in_4bit
        self.args.load_in_8bit = load_in_8bit
        self.args.use_mm_start_end = True
        self.args.local_rank = 0
        
        # Create tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.args.version,
            cache_dir=None,
            model_max_length=self.args.model_max_length,
            padding_side="right",
            use_fast=False,
        )
        self.tokenizer.pad_token = self.tokenizer.unk_token
        self.args.seg_token_idx = self.tokenizer("[SEG]", add_special_tokens=False).input_ids[0]

        # Set torch dtype
        torch_dtype = torch.float32
        if self.args.precision == "bf16":
            torch_dtype = torch.bfloat16
        elif self.args.precision == "fp16":
            torch_dtype = torch.half

        # Set up quantization
        kwargs = {"torch_dtype": torch_dtype}
        if self.args.load_in_4bit:
            kwargs.update({
                "torch_dtype": torch.half,
                "load_in_4bit": True,
                "quantization_config": BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    llm_int8_skip_modules=["visual_model"],
                ),
            })
        elif self.args.load_in_8bit:
            kwargs.update({
                "torch_dtype": torch.half,
                "quantization_config": BitsAndBytesConfig(
                    llm_int8_skip_modules=["visual_model"],
                    load_in_8bit=True,
                ),
            })

        # Load model
        self.model = LISAForCausalLM.from_pretrained(
            self.args.version, 
            low_cpu_mem_usage=True, 
            vision_tower=self.args.vision_tower, 
            seg_token_idx=self.args.seg_token_idx, 
            **kwargs
        )

        self.model.config.eos_token_id = self.tokenizer.eos_token_id
        self.model.config.bos_token_id = self.tokenizer.bos_token_id
        self.model.config.pad_token_id = self.tokenizer.pad_token_id

        self.model.get_model().initialize_vision_modules(self.model.get_model().config)
        vision_tower = self.model.get_model().get_vision_tower()
        vision_tower.to(dtype=torch_dtype)

        # Move model to appropriate precision and device
        if self.args.precision == "bf16":
            self.model = self.model.bfloat16().cuda()
        elif self.args.precision == "fp16" and (not self.args.load_in_4bit) and (not self.args.load_in_8bit):
            vision_tower = self.model.get_model().get_vision_tower()
            self.model.model.vision_tower = None
            try:
                import deepspeed
                model_engine = deepspeed.init_inference(
                    model=self.model,
                    dtype=torch.half,
                    replace_with_kernel_inject=True,
                    replace_method="auto",
                )
                self.model = model_engine.module
                self.model.model.vision_tower = vision_tower.half().cuda()
            except ImportError:
                print("DeepSpeed not available, using regular half precision")
                self.model = self.model.half().cuda()
                self.model.model.vision_tower = vision_tower.half().cuda()
        elif self.args.precision == "fp32":
            self.model = self.model.float().cuda()

        vision_tower = self.model.get_model().get_vision_tower()
        vision_tower.to(device=self.args.local_rank)

        # Initialize processors
        self.clip_image_processor = CLIPImageProcessor.from_pretrained(self.model.config.vision_tower)
        self.transform = ResizeLongestSide(self.args.image_size)
        
        self.model.eval()
        print("Model initialized successfully!")

    def preprocess_image(self, x, img_size=1024):
        """Normalize pixel values and pad to a square input."""
        pixel_mean = torch.Tensor([123.675, 116.28, 103.53]).view(-1, 1, 1)
        pixel_std = torch.Tensor([58.395, 57.12, 57.375]).view(-1, 1, 1)
        
        # Normalize colors
        x = (x - pixel_mean) / pixel_std
        # Pad
        h, w = x.shape[-2:]
        padh = img_size - h
        padw = img_size - w
        x = F.pad(x, (0, padw, 0, padh))
        return x

    def segment_image(self, image, prompt):
        """Perform segmentation on the input image with the given prompt"""
        if self.model is None:
            return None, "Model not initialized. Please wait for initialization to complete."
        
        if image is None:
            return None, "Please upload an image."
        
        if not prompt.strip():
            prompt = "Where is the object in the image? Please output the segmentation mask."

        try:
            # Convert PIL image to numpy array
            image_np = np.array(image)
            if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                # Already RGB
                pass
            else:
                return None, "Invalid image format. Please upload an RGB image."

            original_size_list = [image_np.shape[:2]]

            # Process image for CLIP
            image_clip = (
                self.clip_image_processor.preprocess(image_np, return_tensors="pt")[
                    "pixel_values"
                ][0]
                .unsqueeze(0)
                .cuda()
            )
            
            if self.args.precision == "bf16":
                image_clip = image_clip.bfloat16()
            elif self.args.precision == "fp16":
                image_clip = image_clip.half()
            else:
                image_clip = image_clip.float()

            # Transform image for segmentation
            image_transformed = self.transform.apply_image(image_np)
            resize_list = [image_transformed.shape[:2]]

            image_tensor = (
                self.preprocess_image(torch.from_numpy(image_transformed).permute(2, 0, 1).contiguous())
                .unsqueeze(0)
                .cuda()
            )
            
            if self.args.precision == "bf16":
                image_tensor = image_tensor.bfloat16()
            elif self.args.precision == "fp16":
                image_tensor = image_tensor.half()
            else:
                image_tensor = image_tensor.float()

            # Prepare conversation
            conv = conversation_lib.conv_templates[self.args.conv_type].copy()
            conv.messages = []

            # Process prompt
            prompt_processed = DEFAULT_IMAGE_TOKEN + "\n" + prompt
            if self.args.use_mm_start_end:
                replace_token = (
                    DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN
                )
                prompt_processed = prompt_processed.replace(DEFAULT_IMAGE_TOKEN, replace_token)

            conv.append_message(conv.roles[0], prompt_processed)
            conv.append_message(conv.roles[1], "")
            prompt_final = conv.get_prompt()

            # Tokenize
            input_ids = tokenizer_image_token(prompt_final, self.tokenizer, return_tensors="pt")
            input_ids = input_ids.unsqueeze(0).cuda()

            # Generate segmentation
            with torch.no_grad():
                output_ids, pred_masks = self.model.evaluate(
                    image_clip,
                    image_tensor,
                    input_ids,
                    resize_list,
                    original_size_list,
                    max_new_tokens=512,
                    tokenizer=self.tokenizer,
                )

            # Process output
            output_ids = output_ids[0][output_ids[0] != IMAGE_TOKEN_INDEX]
            text_output = self.tokenizer.decode(output_ids, skip_special_tokens=False)
            text_output = text_output.replace("\n", "").replace("  ", " ")

            # Create visualization
            if len(pred_masks) > 0 and pred_masks[0].shape[0] > 0:
                pred_mask = pred_masks[0].detach().cpu().numpy()[0]
                pred_mask = pred_mask > 0

                # Create masked image
                save_img = image_np.copy()
                if pred_mask.any():
                    # Apply red overlay to segmented areas
                    save_img[pred_mask] = (
                        image_np * 0.5
                        + pred_mask[:, :, None].astype(np.uint8) * np.array([255, 0, 0]) * 0.5
                    )[pred_mask]
                
                result_image = Image.fromarray(save_img.astype(np.uint8))
                return result_image, f"Segmentation completed. Model output: {text_output}"
            else:
                return image, f"No segmentation mask generated. Model output: {text_output}"

        except Exception as e:
            return None, f"Error during segmentation: {str(e)}"

# Initialize the segmentor
segmentor = LISASegmentor()
model_initialized = False
initialization_lock = threading.Lock()

def initialize_model_at_startup():
    """Initialize the model at startup"""
    global model_initialized
    print("🚀 Initializing LISA model at startup...")
    try:
        segmentor.initialize_model()
        model_initialized = True
        print("✅ Model initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing model: {str(e)}")
        model_initialized = False
        return False

def get_model_status():
    """Get current model status"""
    if model_initialized:
        return "✅ Model is ready! Upload an image and start segmenting."
    else:
        return "⏳ Model is initializing... Please wait."

def segment_interface(image, prompt):
    """Interface function for Gradio"""
    if not model_initialized:
        return None, "❌ Model is still initializing. Please wait and try again."
    
    result_image, message = segmentor.segment_image(image, prompt)
    return result_image, message

# Initialize model at startup (in background thread)
def initialize_in_background():
    """Initialize model in background thread"""
    initialize_model_at_startup()

# Start initialization in background
initialization_thread = threading.Thread(target=initialize_in_background, daemon=True)
initialization_thread.start()

# Create Gradio interface
with gr.Blocks(title="LISA Image Segmentation", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎯 LISA Image Segmentation Interface
    
    Upload an image and provide a text prompt to get semantic segmentation results.
    The segmented areas will be highlighted in red overlay.
    
    **Note:** The model is automatically initializing in the background when you start the server.
    Please wait for the initialization to complete before using the interface.
    """)
    
    with gr.Row():
        with gr.Column():
            # Model status (no manual initialization needed)
            model_status = gr.Textbox(
                label="Model Status",
                value="⏳ Model is initializing... Please wait.",
                interactive=False
            )
            
            # Input components
            image_input = gr.Image(
                label="Upload Image",
                type="pil",
                height=400
            )
            
            prompt_input = gr.Textbox(
                label="Segmentation Prompt",
                placeholder="Enter your prompt here (e.g., 'segment the dog', 'where is the car?')",
                value="Where is the object in the image? Please output the segmentation mask.",
                lines=3
            )
            
            segment_button = gr.Button("🎯 Segment Image", variant="primary", size="lg")
            refresh_status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
        
        with gr.Column():
            # Output components
            image_output = gr.Image(
                label="Segmentation Result",
                height=400
            )
            
            result_text = gr.Textbox(
                label="Status & Model Output",
                lines=5,
                interactive=False
            )
    
    # Examples
    gr.Markdown("### 📝 Example Prompts:")
    gr.Examples(
        examples=[
            "Where is the person in the image?",
            "Segment the dog",
            "Where is the car?",
            "Please segment the cat",
            "Find and segment the building",
            "Where are the trees?",
            "Segment the face of the person"
        ],
        inputs=prompt_input
    )
    
    # Event handlers
    refresh_status_btn.click(
        fn=get_model_status,
        outputs=model_status
    )
    
    segment_button.click(
        fn=segment_interface,
        inputs=[image_input, prompt_input],
        outputs=[image_output, result_text]
    )
    
    # Allow Enter key to trigger segmentation
    prompt_input.submit(
        fn=segment_interface,
        inputs=[image_input, prompt_input],
        outputs=[image_output, result_text]
    )
    
    # Load initial status when page loads
    demo.load(
        fn=get_model_status,
        outputs=model_status
    )

if __name__ == "__main__":
    # Enable queue for better handling of concurrent requests
    demo.queue(max_size=20)  # Allow up to 20 requests in queue
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )