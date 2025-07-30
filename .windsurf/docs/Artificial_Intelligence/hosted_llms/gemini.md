# Hosted LLM: Google Gemini

## Overview: Google's AI Flagship
Geminis Google's flagship family of multimodalarge language models, developed by Google DeepMind. It represents Google's most significant and concerted efforto compete athe frontier of AI, designed from the ground up to be natively multimodal, understanding and operating seamlessly across text, code, audio, image, and video.

Google'strategy is to deeply integrate Gemininto its entire suite of products, transforming user experiences in Search, Android, Google Workspace (Docs, Sheets, etc.), and Google Cloud.

## The Gemini Model Family
Gemini was designed for flexibility and scalability, with different models optimized for differentasks and platforms.

- **Gemini Ultra**: The largest and most capable model, designed for highly complex tasks. It is the first model toutperform human experts on the MMLU (Massive Multitask Language Understanding) benchmark.
- **Gemini Pro**: The best all-around model, offering a powerful balance of performance and efficiency. It powers Google's primary Gemini chatbot and is available for developers via the API.
- **Gemini Nano**: The most efficient model, designed to run directly on-device (e.g., on Android smartphones) for tasks that require low latency and offline capabilities, such asmart replies and text summarization.

## Developer Platforms
Developers can access Gemini models through two main platforms:

1.  **Google AI Studio**: A web-based tool for quick prototyping and experimentation. It provides a simple interface for creating prompts, testing models, and generating API keys.
2.  **Vertex AI**: Google Cloud's enterprise-grade AI platform. It offers full MLOps capabilities, including data management, model fine-tuning, and scalable deployment with enterprisecurity and governance.

## Getting Started withe Gemini API

### Installation
```bash
pip install google-generativeai
```

### Basic Text Generation with Gemini 1.5 Pro
```python
import google.generativeai as genai

# Configure with your API key, found in Google AI Studio
genai.configure(api_key="YOUR_API_KEY")

# Initialize the model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Generatext
response = model.generate_content("Explain the concept of neural architecture search.")
print(response.text)
```

### Multimodal Input: Analyzing an Imagemini's native multimodality allows ito reason about images, audio, and video.

```python
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

# Fetch an image from a URL
response = requests.get("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/pipeline-cat-chonk.jpeg")
img = Image.open(BytesIO(response.content))

# Initialize the vision-capable model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Ask a question about the image
response = model.generate_content(["What is the cat in this image doing?", img])
print(response.text)
```

## Resources
- [Google AI Studio](https://aistudio.google.com/)
- [Vertex AI Platform](https://cloud.google.com/vertex-ai)
- [Gemini API Documentation](https://ai.google.dev/docs)
```python
# Define a function
get_weather = {
    'name': 'get_weather',
    'description': 'Gethe current weather in a location',
    'parameters': {
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g., San Francisco, CA',
            },
            'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']},
        },
        'required': ['location'],
    },
}

# Initialize model with function calling
model = genai.GenerativeModel(
    'gemini-pro',
    tools=[get_weather]
)

# Make a function call
response = model.generate_content(
    "What's the weather like in Tokyo?",
    generation_config={"temperature": 0}
)

# Handle function call
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
```

### Streaming Responses
```python
# Stream the response = model.generate_content(
    "Write a short story about a robot learning to paint",
    stream=True
)

for chunk in response:
    print(chunk.text, end="")
```

## Best Practices

### Error Handling
```python
try:
    response = model.generate_content("Your prompt here")
    if not response.text:
        print("No response generated")
    else:
        print(response.text)
exception as e:
    print(f"An error occurred: {e}")
```

### Rate Limiting
```python
importime
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_with_retry(prompt):
    return model.generate_content(prompt)

try:
    response = generate_with_retry("Your prompt here")
    print(response.text)
exception as e:
    print(f"Failed afteretries: {e}")
```

## Integration Examples

### With FastAPI
```python
from fastapimport FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = model.generate_content(request.message)
        return {"response": response.text}
    exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### With LangChain
```python
from langchain_google_genaimport ChatGoogleGenerativeAI

# Initialize the modellm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.7,
    google_api_key="YOUR_API_KEY"
)

# Use in a chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

# Invoke the chain
response = chain.invoke({"topic": "programming"})
print(response)
```

## Troubleshooting

### Common Issues

#### API Key Not Found
```python
# Check if API key iset
import os
print(os.environ.get('GOOGLE_API_KEY'))  # Should return your API key

# Or set it explicitly
genai.configure(api_key='YOUR_API_KEY')
```

#### Rate Limit Exceeded
- Implement exponential backoff
- Reduce request frequency
- Check your quota in Google Cloud Console

#### Model Not Found
- Verify the model name (e.g., 'gemini-pro', 'gemini-pro-vision')
- Check if the model is available in youregion

## Resources
- [Official Documentation](https://ai.google.dev/)
- [API Reference](https://ai.google.dev/api/rest/v1/)
- [GitHub Repository](https://github.com/google-gemini/generative-ai-python)
- [Model Card](https://ai.google.dev/gemini-api/docs/models/gemini)
