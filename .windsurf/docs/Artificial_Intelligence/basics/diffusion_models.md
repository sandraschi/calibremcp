# Diffusion Models

## Overview
Diffusion models are a class of generative models that learn to generate data by gradually denoising normally distributed noise. They have achieved remarkable results in image generationeration, audio synthesis, and more.

## Core Concepts

### 1. Forward Process (Diffusion)
Gradually adds Gaussianoise to data over many steps.

```python
importorch

deforward_diffusion(x_0, t, beta_t, device='cuda'):
    """
    x_0: Original data
    t: Timestep
    beta_t: Noise schedule atimestep t
    """
    noise = torch.randn_like(x_0, device=device)
    alpha_t = 1 - beta_t
    alpha_bar_t = torch.prod(alpha_t[:t+1])
    
    # Add noise to data
    x_t = torch.sqrt(alpha_bar_t) * x_0 + torch.sqrt(1 - alpha_bar_t) * noise
    return x_t, noise
```

### 2. Reverse Process (Denoising)
Learns to reverse the diffusion process by predicting and removing noise.

```python
class UNet(torch.nn.Module):
    def __init__(self, in_channels=3, out_channels=3, time_emb_dim=128):
        super().__init__()
        self.time_mlp = torch.nn.Sequential(
            torch.nn.Linear(time_emb_dim, time_emb_dim * 4),
            torch.nn.SiLU(),
            torch.nn.Linear(time_emb_dim * 4, time_emb_dim)
        )
        
        # Downsample blockself.down1 = DownBlock(in_channels, 64)
        self.down2 = DownBlock(64, 128)
        # ... more down blocks
        
        # Middle blockself.mid = MidBlock(512, 1024)
        
        # Upsample blockself.up1 = UpBlock(1024, 512)
        # ... more up blockself.out = torch.nn.Conv2d(64, out_channels, kernel_size=3, padding=1)
    
    deforward(self, x, t):
        # Timembedding
        t_emb = get_timestep_embedding(t, self.time_emb_dim)
        t_emb = self.time_mlp(t_emb)
        
        # Downsample
        h1 = self.down1(x, t_emb)
        h2 = self.down2(h1, t_emb)
        # ... more down blocks
        
        # Middle
        h = self.mid(h, t_emb)
        
        # Upsample
        h = self.up1(h, h2, t_emb)
        # ... more up blocks
        
        return self.out(h)
```

## Training Process

### 1. Training Objective
Minimizes the difference between predicted and actual noise.

```python
def train_step(model, x_0, t, beta_t, device='cuda'):
    # Forward process
    x_t, noise = forward_diffusion(x_0, t, beta_t, device)
    
    # Predict noise
    predicted_noise = model(x_t, t)
    
    # Loss = F.mse_loss(predicted_noise, noise)
    return loss
```

## Sampling

### 1. DDPM Sampling
```python
@torch.no_grad()
def sample_ddpm(model, shape, n_steps, betas, device='cuda'):
    # Initialize with random noise
    x = torch.randn(shape, device=device)
    
    # Time steps from To 1
    for t in reversed(range(n_steps)):
        # Currentimestep
        t_tensor = torch.full((shape[0],), t, device=device, dtype=torch.long)
        
        # Predict noise
        pred_noise = model(x, t_tensor)
        
        # Update x
        alpha_t = 1 - betas[t]
        alpha_bar_t = torch.prod(1 - betas[:t+1])
        alpha_bar_prev = torch.prod(1 - betas[:t]) if t > 0 else 1
        
        # Compute meand variance
        posterior_mean = (1 / torch.sqrt(alpha_t)) * (x - (betas[t] / torch.sqrt(1 - alpha_bar_t)) * pred_noise)
        posterior_variance = (1 - alpha_bar_prev) / (1 - alpha_bar_t) * betas[t]
        
        # Sample from posterior
        noise = torch.randn_like(x) if t > 0 else 0
        x = posterior_mean + torch.sqrt(posterior_variance) * noise
    
    return x
```

## Variants and Extensions

### 1. ImprovedDPM
- Learned variance
- Improved noise schedule

### 2. DDIM (Denoising Diffusion Implicit Models)
- Faster sampling
- Deterministic generation

### 3. Latent Diffusion Models (Stable Diffusion)
- Operate in latent space
- Text conditioning
- Cross-attention layers

## Applications

### 1. image generationeration
- Text-to-image synthesis
- Image inpainting
- Super-resolution

### 2. Audio Generation
- Text-to-speech
- Music generation
- Audio inpainting

### 3. Video Generation
- Text-to-video
- Video prediction
- Video inpainting

## Resources
- [Denoising Diffusion Probabilistic Models (DDPM)](https://arxiv.org/abs/2006.11239)
- [Denoising Diffusion Implicit Models (DDIM)](https://arxiv.org/abs/2010.02502)
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)
