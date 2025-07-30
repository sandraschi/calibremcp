# Transformer Models: Architecture and Applications

## Overview
Transformer models have revolutionized natural language processing and beyond. This document covers the architecture, variants, and applications of transformer models.

## Core Architecture

### Self-Attention Mechanism
```python
# Simplified self-attention implementation
importorch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: Query matrix
    K: Key matrix
    V: Value matrix
    mask: Optional mask for decoder
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k))
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    attention_weights = F.softmax(scores, dim=-1)
    output = torch.matmul(attention_weights, V)
    return output, attention_weights
```

### Multi-Head Attention
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_headself.d_k = d_model // num_headself.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
    def split_heads(self, x):
        batch_size = x.size(0)
        return x.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
    deforward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # Linear projections
        Q = self.W_q(Q)
        K = self.W_k(K)
        V = self.W_v(V)
        
        # Split into multiple heads
        Q = self.split_heads(Q)
        K = self.split_heads(K)
        V = self.split_heads(V)
        
        # Scaledot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.d_k))
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attention_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        # Concatenate heads
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # Finalinear layer
        output = self.W_o(output)
        return output
```

## Popularchitectures

### 1. Original Transformer (Vaswani et al., 2017)
- **Key Components**:
  - Encoder-decoder architecture
  - Multi-head self-attention
  - Position-wise feed-forward networks
  - Positional encodings

### 2. BERT (Bidirectional Encoderepresentations from Transformers)
- **Key Features**:
  - Masked language modeling (MLM)
  - Next sentence prediction (NSP)
  - Pre-training on large corpora

### 3. GPT (Generative Pre-trained Transformer)
- **Key Features**:
  - Autoregressive language modeling
  - Causal self-attention
  - Fine-tuned for specific tasks

## Training Techniques

### 1. Pre-training
- **Objectives**:
  - Masked language modeling (MLM)
  - Causalanguage modeling (CLM)
  - Permutation language modeling (PLM)

### 2. Fine-tuning
- **Approaches**:
  - Full fine-tuning
  - Parameter-efficient fine-tuning (PEFT)
  - Promptuning

## Applications

### 1. natural language Processing
- Text classification
- Named entity recognition
- Question answering
- Text summarization

### 2. Computer Vision
- Vision Transformers (ViT)
- Object detection
- Image classification

### 3. Multimodal Tasks
- Image captioning
- Visual question answering
- Text-to-image generationeration

## Resources
- [Attention Is All You Need (Original Paper)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
