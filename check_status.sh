#!/bin/bash

echo "🔍 Local LLM System Status Check"
echo "================================="

# Check models
echo "📁 Checking models..."
if [ -f "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
    size=$(du -h "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" | cut -f1)
    echo "   ✅ TinyLlama: $size"
else
    echo "   ❌ TinyLlama: missing"
fi

if [ -d "models/mistral" ]; then
    file_count=$(ls -1 models/mistral/ 2>/dev/null | wc -l)
    if [ $file_count -gt 0 ]; then
        total_size=$(du -sh models/mistral/ | cut -f1)
        echo "   ⚠️  Mistral: $file_count files, $total_size"
    else
        echo "   ❌ Mistral: empty directory"
    fi
else
    echo "   ❌ Mistral: missing"
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
if python -c "import torch" 2>/dev/null; then
    echo "   ✅ torch"
else
    echo "   ❌ torch"
fi

if python -c "import transformers" 2>/dev/null; then
    echo "   ✅ transformers"
else
    echo "   ❌ transformers"
fi

if python -c "from llama_cpp import Llama" 2>/dev/null; then
    echo "   ✅ llama-cpp-python"
else
    echo "   ❌ llama-cpp-python"
fi

if python -c "import redis" 2>/dev/null; then
    echo "   ✅ redis"
else
    echo "   ❌ redis"
fi

if python -c "import pymongo" 2>/dev/null; then
    echo "   ✅ pymongo"
else
    echo "   ❌ pymongo"
fi

# Check hardware
echo ""
echo "🖥️  Checking hardware..."
cpu_cores=$(nproc)
echo "   ✅ CPU: $cpu_cores cores"

memory_gb=$(free -g | awk '/^Mem:/{print $2}')
echo "   ✅ Memory: ${memory_gb}GB"

if command -v nvidia-smi &> /dev/null; then
    gpu_info=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null)
    if [ $? -eq 0 ]; then
        gpu_name=$(echo "$gpu_info" | cut -d',' -f1 | xargs)
        gpu_memory=$(echo "$gpu_info" | cut -d',' -f2 | xargs)
        echo "   ✅ GPU: $gpu_name (${gpu_memory}MB)"
    else
        echo "   ❌ GPU: not detected"
    fi
else
    echo "   ❌ GPU: nvidia-smi not available"
fi

echo ""
echo "================================="
echo "Status check completed!" 