# Stable Diffusion: Advanced image generationeration

## Introduction
Stable Diffusion is a powerful open-source text-to-image generationeration model that has revolutionized AI art creation. This document provides a comprehensive guide to using and customizing Stable Diffusion for various applications.

## 1. Core Concepts

### 1.1 Architecture Overview
- Latent Diffusion Models (LDM)
- U-Net architecture
- CLIP text encoder
- VAE (Variational Autoencoder)

### 1.2 Key Features
- Text-to-image generationeration
- Image-to-image translation
- Inpainting and outpainting
- Image upscaling
- Model fine-tuning

## 2. Getting Started

### 2.1 Installation
```powershell
# Create and activate conda environment
conda create -n sd python=3.10 -y
condactivate sd

# Install PyTorch with CUDA support
pip3 install torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install diffusers and transformers
pip install diffusers transformers accelerate

# For xformers (optional, for better performance)
pip install xformers

# For image processing
pip install pillow numpy
```

### 2.2 Basic Usage
```python
from diffusers import StableDiffusionPipeline
importorch

# Load the pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    safety_checker=None  # Disable safety checker for NSFW content
).to("cuda")

# Enable attention slicing for lower memory usage
pipe.enable_attention_slicing()

# Generate an image
prompt = "A beautiful sunset over mountains, highly detailed, digital art"
image = pipe(prompt).images[0]
image.save("sunset.png")
```

## 3. Advanced Features

### 3.1 Image-to-Image
```python
from PIL import Image

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

init_image = Image.open("input.jpg").convert("RGB")
init_image = init_image.resize((512, 512))

prompt = "A fantasy landscape with a castle"
image = pipe(
    prompt=prompt,
    image=init_image,
    strength=0.75,  # 0-1: how much to transform the image
    guidance_scale=7.5,
    num_inference_steps=50
).images[0]

image.save("fantasy_landscape.png")
```

### 3.2 Inpainting
```python
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image, ImageDraw
import numpy as npipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16,
).to("cuda")

# Load and prepare the image and mask
image = Image.open("image.png").convert("RGB").resize((512, 512))
mask = Image.new("L", (512, 512), 0)
draw = ImageDraw.Draw(mask)
draw.rectangle([100, 100, 400, 400], fill=255)  # Area to inpaint

prompt = "A vase with flowers"
result = pipe(
    prompt=prompt,
    image=image,
    mask_image=mask,
    strength=0.8,
    num_inference_steps=50,
).images[0]

result.save("inpainted.png")
```

## 4. Model Fine-tuning

### 4.1 Textual Inversion
```python
from diffusers import StableDiffusionPipeline, TextualInversionLoaderMixin

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
).to("cuda")

# Load the learned embedding
pipe.load_textual_inversion("sd-concepts-library/cat-toy")

# Use the special placeholder in your prompt
image = pipe("A <cat-toy> in a field oflowers").images[0]
image.save("cat_toy.png")
```

### 4.2 Dreambooth
```python
# Requires the diffusers training scripts
!git clone https://github.com/huggingface/diffusers
%cdiffusers/examples/dreambooth

# Install requirements
!pip install -requirements.txt

# Download and prepare dataset
!wget https://example.com/your_images.zip
!unzip your_images.zip -dataset

# Startraining
!accelerate launch train_dreambooth.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
  --instance_data_dir="dataset" \
  --output_dir="model_output" \
  --instance_prompt="a photof sks person" \
  --resolution=512 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --learning_rate=2e-6 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --max_train_steps=400
```

## 5. Performance Optimization

### 5.1 Using xformers
```python
pipe.enable_xformers_memory_efficient_attention()
```

### 5.2 Model Offloading
```python
pipe.enable_model_cpu_offload()
```

### 5.3 Using FP16/FP8
```python
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,  # or torch.bfloat16 if supported
).to("cuda")
```

## 6. Advanced Techniques

### 6.1 ControlNet
```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
import cv2
import numpy as np

# Load control net and model
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("cuda")

# Process input image = load_image("input.png")
image = np.array(image)
low_threshold = 100
high_threshold = 200
image = cv2.Canny(image, low_threshold, high_threshold)
image = image[:, :, None]
image = np.concatenate([image, image, image], axis=2)
image = Image.fromarray(image)

# Generate image
prompt = "a futuristicity"
output = pipe(
    prompt,
    image=image,
    num_inference_steps=20,
).images[0]

output.save("controlled_generation.png")
```

## 7. Web UInstallation (Automatic1111)

### 7.1 Windowsetup
```powershell
# Clone the repository
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# Run the web UI
.\webui-user.bat
```

### 7.2 Key Features
- Intuitive browser interface
- Multiple samplers
- Extensionsystem
- Built-in upscaling
- Embedding/Textual Inversion support
- X/Y/Z plot for parameter testing

## 8. Model Management

### 8.1 Downloading Models
- CivitAI (https://civitai.com/)
- Hugging Face Model Hub (https://huggingface.co/models)
- Official Stability AI releases

### 8.2 Model Formats
- .ckpt (Checkpoint)
- .safetensors (Recommended, safer format)
- Diffusers (Hugging Face format)

## 9. Ethical Considerations

### 9.1 Copyright and Fair Use
- Respect artist rights
- Check modelicenses
- Be transparent about AI generation

### 9.2 Safety Measures
- Content filtering
- NSFW detection
- Watermarking

## 10. Resources

### 10.1 Official Documentation
- [Stable Diffusion GitHub](https://github.com/CompVis/stable-diffusion)
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers/index)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 10.2 Community Resources
- [r/StableDiffusion](https://www.reddit.com/r/StableDiffusion/)
- [CivitAI Forums](https://civitai.com/)
- [Hugging Face Community](https://huggingface.co/)

### 10.3 Tutorials
- [Hugging Face Course](https://huggingface.co/course/chapter1)
- [Stable Diffusion with 🧨 Diffusers](https://huggingface.co/docs/diffusers/using-diffusers/stable_diffusion)
- [The Last Ben's Notebooks](https://github.com/TheLastBen/fast-stable-diffusion)
