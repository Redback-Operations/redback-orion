# LISA: Reasoning Segmentation via Large Language Model and Heatmap generate by CSRNet


## Introduction
This repository leverages **LISA** for audience segmentation and **CSRNet** for heatmap generation.  
- Use `app.py` to run the API.  
- Use `lisa_gradio_interface.py` to launch a Gradio-based interface.  

If you have any questions about this project, feel free to contact me at buisontung2310@gmail.com.

## Installation
```
git clone https://github.com/sontung2310/LISA.git
cd LISA
conda create -n lisa python=3.9
pip install -r requirements.txt
pip install flash-attn --no-build-isolation
```

Download the weight from [this link](https://drive.google.com/file/d/1Ti_DQ0lYXCLqhH9nGwtMMWH5Zt5xiJA2/view?pli=1) and save it into the `csrnet/` folder.


## Inference 

```
CUDA_VISIBLE_DEVICES=0 python chat.py --version='xinlai/LISA-13B-llama2-v1'
CUDA_VISIBLE_DEVICES=0 python chat.py --version='xinlai/LISA-13B-llama2-v1-explanatory'
```
To use `bf16` or `fp16` data type for inference:
```
CUDA_VISIBLE_DEVICES=0 python chat.py --version='xinlai/LISA-13B-llama2-v1' --precision='bf16'
```
To use `8bit` or `4bit` data type for inference (this enables running 13B model on a single 24G or 12G GPU at some cost of generation quality):
```
CUDA_VISIBLE_DEVICES=0 python chat.py --version='xinlai/LISA-13B-llama2-v1' --precision='fp16' --load_in_8bit
CUDA_VISIBLE_DEVICES=0 python chat.py --version='xinlai/LISA-13B-llama2-v1' --precision='fp16' --load_in_4bit
```
Hint: for 13B model, 16-bit inference consumes 30G VRAM with a single GPU, 8-bit inference consumes 16G, and 4-bit inference consumes 9G.

After that, input the text prompt and then the image path. For example，
```
- Please input your prompt: Where can the driver see the car speed in this image? Please output segmentation mask.
- Please input the image path: imgs/example1.jpg

- Please input your prompt: Can you segment the food that tastes spicy and hot?
- Please input the image path: imgs/example2.jpg
```
The results should be like:
<p align="center"> <img src="imgs/example1.jpg" width="22%"> <img src="vis_output/example1_masked_img_0.jpg" width="22%"> <img src="imgs/example2.jpg" width="25%"> <img src="vis_output/example2_masked_img_0.jpg" width="25%"> </p>

To run the gradio interface (load in 8bit and fp16):
```
python lisa_gradio_interface.py 
```

Run the API
```
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Acknowledgement
-  This work is built upon the [LLaVA](https://github.com/haotian-liu/LLaVA) and [SAM](https://github.com/facebookresearch/segment-anything). 
