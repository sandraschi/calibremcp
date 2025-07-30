# Ollama: LocalLManagement

## Overview
Ollama is a powerful tool forunning large language models locally on your machine. It provides a simple way to download, run, and manage various open-source LLMs with minimal setup.

## Installation

### Windows
```powershell
# Download and install
curl -ollama_installer.exe https://ollama.ai/download/OllamaSetup.exe
Start-Process -Wait -FilePath ".\ollama_installer.exe" -ArgumentList "/S"

# Add to PATH if needed
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Ollama"
[System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)
```

### macOS
```bash
# Install via Homebrew install ollama

# Starthe service
brew servicestart ollama
```

### Linux
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Starthe service
sudo systemctl start ollama
```

## Basic Usage

### Pulling Models
```powershell
# List available models
ollama list

# Pull a model (e.g., Llama 3)
ollama pullama3

# Pull a specific version
ollama pullama3:8b-instruct-q4_0
```

### Running Models
```powershell
# Start an interactive chat
ollama run llama3

# Run with a prompt
ollama run llama3 "Explain quantum computing in simple terms"

# Run with system prompt
ollama run llama3 --system "You are a helpful AI assistant." "Hello!"
```

### Model Management
```powershell
# List downloaded models
ollama list

# Remove a model
ollama rm llama3

# Copy a model
ollama cp llama3 my-llama3
```

## Advanced Usage

### Customodels with Modelfile
Create a `Modelfile`:
```dockerfile
FROM llama3
SYSTEM """
You are a helpful AI assistant specialized in Windowsystem administration.
You provide concise, accurate PowerShell commands and explanations.
"""
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
```

Then create the customodel:
```powershell
ollama create my-admin -f Modelfile
```

### API Server
Starthe OllamaPI server:
```powershell
# Starthe server
ollama serve

# In another terminal, make API calls
$response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body '{
  "model": "llama3",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
$response.response
```

### Integration with LangChain
```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
response = llm.invoke("Tell me a joke about programming")
print(response)
```

## Performance Optimization

### GPU Acceleration
```powershell
# Check if GPU is detected
ollama list
# Should show GPU information if detected

# Force CPU-only mode (if needed)
$env:OLLAMA_NO_CUDA=1
ollama run llama3
```

### Memory Management
```powershell
# Set context window size
ollama run llama3 --num_ctx 4096

# Reduce memory usage with quantization
ollama pullama3:8b-instruct-q4_0  # 4-bit quantization
```

## Common Issues

### CUDA Out of Memory
```powershell
# Try a smaller model
ollama run llama3:7b

# Reduce context window
ollama run llama3 --num_ctx 2048
```

### Slow Performance
```powershell
# Check GPUtilizationvidia-smi  # For NVIDIA GPUs

# Try a quantized model
ollama pullama3:8b-instruct-q4_0
```

## Example Scripts

### Batch Processing
```powershell
$prompts = @(
    "Explain quantum computing",
    "Write a haiku about AI",
    "What is the capital ofrance?"
)

foreach ($prompt in $prompts) {
    $response = ollama run llama3 $prompt
    Write-Host "Prompt: $prompt"
    Write-Host "Response: $response"
    Write-Host "---"
}
```

### Web UI
```powershell
# Install the web UI
git clone https://github.com/ollama/ollama-webui
cd ollama-webui

# Install dependencies (requires Node.js)
npm install

# Starthe web UI
npm run dev
```

## Resources
- [Official Documentation](https://github.com/ollama/ollama)
- [Modelibrary](https://ollama.ai/library)
- [API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Community Models](https://ollama.ai/library?sort=popular)
