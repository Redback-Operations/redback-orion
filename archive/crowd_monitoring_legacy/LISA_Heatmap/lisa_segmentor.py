import argparse
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoTokenizer, BitsAndBytesConfig, CLIPImageProcessor

from model.LISA import LISAForCausalLM
from model.llava import conversation as conversation_lib
from model.llava.mm_utils import tokenizer_image_token
from model.segment_anything.utils.transforms import ResizeLongestSide
from utils.utils import (
    DEFAULT_IM_END_TOKEN,
    DEFAULT_IM_START_TOKEN,
    DEFAULT_IMAGE_TOKEN,
    IMAGE_TOKEN_INDEX,
)


class LISASegmentor:
    """Headless LISA segmentor for programmatic use (no Gradio side effects)."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.clip_image_processor = None
        self.transform = None
        self.args = None

    def initialize_model(
        self,
        version="xinlai/LISA-13B-llama2-v1",
        precision="fp16",
        image_size=1024,
        model_max_length=512,
        vision_tower="openai/clip-vit-large-patch14",
        conv_type="llava_v1",
        load_in_4bit=True,
        load_in_8bit=False,
        device: str = "cuda",
    ) -> None:
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

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.args.version,
            cache_dir=None,
            model_max_length=self.args.model_max_length,
            padding_side="right",
            use_fast=False,
        )
        self.tokenizer.pad_token = self.tokenizer.unk_token
        self.args.seg_token_idx = self.tokenizer("[SEG]", add_special_tokens=False).input_ids[0]

        # Dtype
        torch_dtype = torch.float32
        if self.args.precision == "bf16":
            torch_dtype = torch.bfloat16
        elif self.args.precision == "fp16":
            torch_dtype = torch.half

        # Quantization
        kwargs = {"torch_dtype": torch_dtype}
        if self.args.load_in_4bit:
            kwargs.update(
                {
                    "torch_dtype": torch.half,
                    "load_in_4bit": True,
                    "quantization_config": BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        llm_int8_skip_modules=["visual_model"],
                    ),
                }
            )
        elif self.args.load_in_8bit:
            kwargs.update(
                {
                    "torch_dtype": torch.half,
                    "quantization_config": BitsAndBytesConfig(
                        llm_int8_skip_modules=["visual_model"],
                        load_in_8bit=True,
                    ),
                }
            )

        # Model
        self.model = LISAForCausalLM.from_pretrained(
            self.args.version,
            low_cpu_mem_usage=True,
            vision_tower=self.args.vision_tower,
            seg_token_idx=self.args.seg_token_idx,
            **kwargs,
        )

        self.model.config.eos_token_id = self.tokenizer.eos_token_id
        self.model.config.bos_token_id = self.tokenizer.bos_token_id
        self.model.config.pad_token_id = self.tokenizer.pad_token_id

        self.model.get_model().initialize_vision_modules(self.model.get_model().config)
        vision_tower = self.model.get_model().get_vision_tower()
        vision_tower.to(dtype=torch_dtype)

        if device == "cuda":
            if self.args.precision == "bf16":
                self.model = self.model.bfloat16().cuda()
            elif self.args.precision == "fp16" and (not self.args.load_in_4bit) and (not self.args.load_in_8bit):
                vision_tower = self.model.get_model().get_vision_tower()
                self.model.model.vision_tower = None
                try:
                    import deepspeed  # type: ignore

                    model_engine = deepspeed.init_inference(
                        model=self.model,
                        dtype=torch.half,
                        replace_with_kernel_inject=True,
                        replace_method="auto",
                    )
                    self.model = model_engine.module
                    self.model.model.vision_tower = vision_tower.half().cuda()
                except Exception:
                    self.model = self.model.half().cuda()
                    self.model.model.vision_tower = vision_tower.half().cuda()
            elif self.args.precision == "fp32":
                self.model = self.model.float().cuda()

            vision_tower = self.model.get_model().get_vision_tower()
            vision_tower.to(device=self.args.local_rank)
        else:
            # CPU fallback (very slow, but functional)
            if self.args.precision == "fp16":
                self.model = self.model.float()
            self.model = self.model.to("cpu")

        self.clip_image_processor = CLIPImageProcessor.from_pretrained(self.model.config.vision_tower)
        self.transform = ResizeLongestSide(self.args.image_size)
        self.model.eval()

    @staticmethod
    def _preprocess_image_for_segmentation(x: torch.Tensor, img_size: int = 1024) -> torch.Tensor:
        pixel_mean = torch.Tensor([123.675, 116.28, 103.53]).view(-1, 1, 1)
        pixel_std = torch.Tensor([58.395, 57.12, 57.375]).view(-1, 1, 1)
        x = (x - pixel_mean) / pixel_std
        h, w = x.shape[-2:]
        padh = img_size - h
        padw = img_size - w
        x = F.pad(x, (0, padw, 0, padh))
        return x

    def segment(self, image: Image.Image, prompt: str) -> np.ndarray:
        """
        Returns a boolean numpy mask (H, W) matching the input image size.
        If no mask is generated, returns an all-false mask.
        """
        if self.model is None:
            raise RuntimeError("LISA model not initialized. Call initialize_model() first.")

        image_np = np.array(image)
        if image_np.ndim != 3 or image_np.shape[2] != 3:
            raise ValueError("Expected an RGB image.")

        original_h, original_w = image_np.shape[:2]

        # CLIP preprocess
        image_clip = (
            self.clip_image_processor.preprocess(image_np, return_tensors="pt")["pixel_values"][0]
            .unsqueeze(0)
        )
        image_clip = image_clip.cuda() if next(self.model.parameters()).is_cuda else image_clip

        if self.args.precision == "bf16":
            image_clip = image_clip.bfloat16()
        elif self.args.precision == "fp16":
            image_clip = image_clip.half()
        else:
            image_clip = image_clip.float()

        # Segmentation transform
        image_transformed = self.transform.apply_image(image_np)
        image_tensor = torch.from_numpy(image_transformed).permute(2, 0, 1).contiguous()
        image_tensor = self._preprocess_image_for_segmentation(image_tensor, self.args.image_size).unsqueeze(0)
        image_tensor = image_tensor.cuda() if next(self.model.parameters()).is_cuda else image_tensor

        if self.args.precision == "bf16":
            image_tensor = image_tensor.bfloat16()
        elif self.args.precision == "fp16":
            image_tensor = image_tensor.half()
        else:
            image_tensor = image_tensor.float()

        # Conversation prompt
        if not prompt or not prompt.strip():
            prompt = "Where is the audience in the image? Output the segmentation mask."

        conv = conversation_lib.conv_templates[self.args.conv_type].copy()
        conv.messages = []
        prompt_processed = DEFAULT_IMAGE_TOKEN + "\n" + prompt
        if self.args.use_mm_start_end:
            replace_token = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN
            prompt_processed = prompt_processed.replace(DEFAULT_IMAGE_TOKEN, replace_token)
        conv.append_message(conv.roles[0], prompt_processed)
        conv.append_message(conv.roles[1], "")
        prompt_final = conv.get_prompt()

        input_ids = tokenizer_image_token(prompt_final, self.tokenizer, return_tensors="pt").unsqueeze(0)
        input_ids = input_ids.cuda() if next(self.model.parameters()).is_cuda else input_ids

        resize_list = [image_transformed.shape[:2]]
        original_size_list = [image_np.shape[:2]]

        with torch.no_grad():
            _, pred_masks = self.model.evaluate(
                image_clip,
                image_tensor,
                input_ids,
                resize_list,
                original_size_list,
                max_new_tokens=512,
                tokenizer=self.tokenizer,
            )

        if len(pred_masks) == 0 or pred_masks[0].shape[0] == 0:
            return np.zeros((original_h, original_w), dtype=bool)

        pred_mask = pred_masks[0].detach().cpu().numpy()[0] > 0
        # Ensure shape to original
        if pred_mask.shape[0] != original_h or pred_mask.shape[1] != original_w:
            pred_mask = np.array(Image.fromarray(pred_mask.astype(np.uint8) * 255).resize((original_w, original_h), Image.NEAREST)) > 0

        return pred_mask


