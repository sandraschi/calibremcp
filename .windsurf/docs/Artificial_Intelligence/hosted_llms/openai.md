# Hosted LLM: OpenAI

## Overview: The Generative AI Pioneer
OpenAIs an AI research andeployment company that has been athe forefront of the generative AI revolution. Its mission is to ensure that artificial general intelligence (AGI) benefits all of humanity. OpenAIs responsible for creating some of the most influential and widely used AI models in the world.

Their most famous creation, **ChatGPT**, broughthe power of large language models to the mainstream, demonstrating their ability to engage in conversation, answer questions, writessays, and generate code.

## Core Products and Models
OpenAI offers a suite of powerful models accessible through its API, each specializing in different domains.

- **GPT-4 & GPT-4o (Omni)**: The latest and most capable generation of Generative Pre-trained Transformers. These models exhibit human-level performance on many professional and academic benchmarks. GPT-4o is natively multimodal, accepting and generating a mix of text, audio, and image inputs and outputs for a more seamless human-computer interaction.
- **DALL-E 3**: A state-of-the-art image generationeration model that can create highly detailed and contextually relevant images from natural language descriptions. It is integrated directly into ChatGPT and is available via the API.
- **Whisper**: An automatic speech recognition (ASR) system trained on a massive dataset of diverse audio. It approaches human-level robustness and accuracy for transcribing speech.
- **Sora**: A text-to-video model capable of generating high-fidelity, realistic, and imaginative video scenes from text instructions.

## Getting Started withe OpenAI API

### Installation
The official Python library provides convenient access to the OpenAI API.

```bash
pip install openai
```

### Example: Chat Completion with GPT-4o
```python
from openaimport OpenAI

# The client automatically looks for the OPENAI_API_KEY environment variable
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a witty assistanthat responds to every query with a rhyming couplet."
        },
        {
            "role": "user",
            "content": "What is the primary function of a CPU in a computer?"
        }
    ]
)

print(response.choices[0].message.content)
```

### Example: image generationeration with DALL-E 3
```python
from openaimport OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A photorealistic image of an astronaut riding a horse on Mars, with Earth visible in the sky.",
    size="1024x1024",
    quality="standard",
    n=1,
)

image_url = response.data[0].url
print(f"Generated image URL: {image_url}")
```

## Resources
- [OpenAI Website](https://openai.com/)
- [OpenAI Blog](https://openai.com/blog)
- [API Documentation](https://platform.openai.com/docs/)
