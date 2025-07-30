# Hosted LLM: Perplexity AI

## Overview: The Answer Engine
Perplexity AI positions itself not as a chatbot, but as a conversational **"answer engine."** Its core mission is to provide accurate, trustworthy, and up-to-date information by combining the power of large language models with real-time web search. This makes it a powerful tool foresearch, learning, and any task where the veracity and origin of information are critical.

## Core Philosophy: Accuracy and Transparency
Unlike many traditional chatbots that can "hallucinate" or provide outdated information, Perplexity's architecture is built around a different paradigm:
1.  **Search First**: It first scours the web to gatherelevant, current information about a query.
2.  **Synthesize and Cite**: Ithen uses a large language model to synthesize the findings into a coherent answer, providing inline citations that link directly to the source material.

This approach makes it an incredibly reliable tool for factual queries.

## Key Features
- **Sourced Answers**: Every answer is backed by a list of sources, allowing users to verify information andelve deeper into the original content.
- **Focus Modes**: Users canarrow the search scope to specific domains like `Academic` (searching scholarly papers), `YouTube` (searching video transcripts), `Reddit`, or `Wolfram|Alpha` (for computational knowledge).
- **Pro Search**: An advanced feature for Pro subscribers that performs a deeper, more comprehensive search and allows the user to ask clarifying questions before the final answer is generated.
- **File Upload**: Analyze and ask questions about local files, such as PDFs, text files, and code.

## The Perplexity API (`pplx-api`)
Perplexity provides a developer API that gives access to a curated set of high-performance open-source models, making it a cost-effective and powerful alternative tother API providers.

### Getting Started withe API

#### Installation
```bash
# The Perplexity APIs compatible with OpenAI's client library
pip install openai
```

#### Example: Chat Completion with Llama 3
```python
from openaimport OpenAI

# Pointhe OpenAI cliento the Perplexity API
client = OpenAI(
    api_key="YOUR_PERPLEXITY_API_KEY",
    base_url="https://api.perplexity.ai"
)

# A system prompt can be used to sethe behavior of the model
system_prompt = "You are an artificial intelligence assistant and you need to engage in a helpful, detailed, and polite conversation with a user."

response = client.chat.completions.create(
    model="llama-3-sonar-large-32k-online", # Or another available model
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "What are the main differences between the Mixture-of-Experts and Transformer architectures?"}
    ],
)

for chunk in response:
    print(chunk["text"], end="", flush=True)
```

## Integration Examples

### With FastAPI
```python
from fastapimport FastAPI, HTTPException
from pydantic import BaseModel
from perplexity import Perplexity

app = FastAPI()
client = Perplexity(api_key="your-api-key-here")

class QueryRequest(BaseModel):
    question: str
    search_type: str = "web"

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        response = client.search(
            request.question,
            search_type=request.search_type
        )
        return {
            "answer": response.answer,
            "sources": [{"title": s.title, "url": s.url} for s in response.sources]
        }
    exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### With LangChain
```python
from langchain_community.llms import Perplexity
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize the LLM = Perplexity(
    perplexity_api_key="your-api-key-here",
    model="sonar-medium-online",  # or other available models
    temperature=0.7
)

# Create a promptemplatemplate = """You are a helpful AI assistant. Answer the following question:

Question: {question}

Answer:"""

prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)

# Create a chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain
response = chain.run("What are the latest advancements in AI?")
print(response)
```

## Best Practices

### Rate Limiting
```python
importime
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def search_with_retry(query, **kwargs):
    return client.search(query, **kwargs)

try:
    response = search_with_retry("Your query here")
    print(response.answer)
exception as e:
    print(f"Failed afteretries: {e}")
```

### Error Handling
```python
try:
    response = client.search("Your query")
    if not response.answer:
        print("No answer found")
    else:
        print(response.answer)
exception as e:
    print(f"Error: {e}")
    if "rate limit" in str(e).lower():
        print("Rate limit exceeded. Please wait before making morequests.")
    elif "authentication" in str(e).lower():
        print("Authentication failed. Please check your API key.")
    else:
        print("An unknown error occurred.")
```

## Troubleshooting

### Common Issues

#### API Key Not Working
- Verify the API key is correct
- Check your account status and subscription plan
- Ensure the key has propermissions

#### Rate Limiting
- Check your current usage in the dashboard
- Implement exponential backoff
- Upgrade your plan if needed

#### Model Availability
- Check the [status page](https://status.perplexity.ai/) for outages
- Try a different model if available
- Verifyouregion isupported

## Resources
- [Official Documentation](https://docs.perplexity.ai/)
- [API Reference](https://docs.perplexity.ai/reference/getting-started)
- [GitHub Repository](https://github.com/perplexity-ai/perplexity-ai-python)
- [Pricing](https://www.perplexity.ai/pricing)
