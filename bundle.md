---
bundle:
  name: llm-guides
  version: 0.1.0
  description: |
    Team knowledge bundle for running Qwen3.5, Qwen3.6, and Gemma 4 locally.

    Covers model selection, hardware requirements (CUDA / ROCm / MLX), and
    backend setup (llama.cpp, Ollama, vLLM, LM Studio) across Windows, Linux,
    and macOS. Includes the infographic-builder bundle for generating visual
    summaries, decision charts, and model comparison cards.

includes:
  - bundle: git+https://github.com/singh2/infographic-builder@main
  - bundle: git+https://github.com/singh2/amplifier-bundle-diagram-beautifier@main
---

@llm-guides:README.md

@llm-guides:models/qwen3.5.md
@llm-guides:models/qwen3.6.md
@llm-guides:models/gemma4.md

@llm-guides:backends/llama-cpp.md
@llm-guides:backends/ollama.md
@llm-guides:backends/vllm.md
@llm-guides:backends/lmstudio.md

@llm-guides:hardware/cuda.md
@llm-guides:hardware/rocm.md
@llm-guides:hardware/mlx.md

@llm-guides:agent-integration.md
