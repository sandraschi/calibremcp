# Hosted LLM: Anthropiclaude

## Overview: AI Safety First
Anthropic is an AI safety and research company dedicated to building reliable, interpretable, and steerable AI systems. Founded by former senior members of OpenAI, Anthropic's core mission is to ensure that advanced AI technologies are developed responsibly and for the benefit of humanity.

Their flagshiproduct is **Claude**, a family of large language models known for their strong performance, large context windows, and, most importantly, their safety-orientedesign.

## Core Philosophy: Constitutional AI
Anthropic's key innovation in AI safety is **Constitutional AI (CAI)**. This a framework for training AI models to be helpful and harmless without relying on extensive human feedback. The process involves:
1.  **A Constitution**: A set of principles and rules (e.g., from the UN Declaration of Human Rights, or other sources) that guide the model's behavior.
2.  **Supervised Learning**: The model is firstrained to critique and revise its own responses based on the constitution.
3.  **Reinforcement Learning**: The model is then trained to prefer the revised, constitutionally-aligned responses.

This approach aims to make the AI's values morexplicit and transparent.

## The Claude 3 Model Family
In early 2024, Anthropic released the Claude 3 family, a suite of models that set new industry benchmarks for intelligence, speed, and vision capabilities.

- **Claude 3 Opus**: The most powerful model, designed for top-tier performance on highly complex tasks. It excels at open-ended conversation, complex analysis, and research.
- **Claude 3 Sonnet**: The best balance of intelligence and speed. It is ideal for enterprise workloads, data processing, and code generation.
- **Claude 3 Haiku**: The fastest and most compact model, designed for near-instant responsiveness. It is perfect for customer service applications, content moderation, and other tasks requiring low latency.

All Claude 3 models have advanced vision capabilities and large context windows (up to 200K tokens).

## Getting Started withe Claude API

### Installation
```bash
pip install anthropic
```

### Example: Chat Completion with Claude 3 Sonnet
```python
import anthropic

# The client automatically looks for the ANTHROPIC_API_KEY environment variable
client = anthropic.Anthropic()

# A system prompt can be used to sethe role and personality of the model
system_prompt = "You are a helpful and friendly assistant who specializes in explaining complex scientific topics to a general audience."

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": "Could you explain the basics of mRNA vaccines?"
        }
    ]
)

print(response.content[0].text)
```

## Resources
- [Anthropic Website](https://www.anthropic.com/)
- [Claude Website](https://www.anthropic.com/claude)
- [API Documentation](https://docs.anthropic.com/)
