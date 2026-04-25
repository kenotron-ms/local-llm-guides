# Quantization & Model Variants

    When you download an LLM locally, you're almost always downloading a **quantized** version — a compressed form of the model that trades a small amount of quality for dramatically smaller file sizes and faster inference. This guide explains the format, naming conventions, and how to pick.

    ---

    ## What Is GGUF?

    **GGUF** (GPT-Generated Unified Format) is the file format used by llama.cpp and compatible runtimes (Ollama, LM Studio, Jan). A single `.gguf` file contains everything needed to run a model: weights, tokenizer, and metadata.

    GGUF replaced the older GGML format in 2023. The key advantages:
    - Single self-contained file (no separate tokenizer or config files)
    - Metadata embedded in the file header — runtimes auto-configure settings
    - Efficient memory mapping — pages load on demand, not all at once
    - CPU + GPU split supported natively — layers can span VRAM and system RAM

    **When you DON'T use GGUF:** vLLM and Hugging Face Transformers use safetensors (`.safetensors`), which is the native format for full-precision GPU inference.

    ---

    ## Quantization: The Core Idea

    A standard model stores each weight as a 16-bit float (BF16 or FP16). Quantization rounds weights to fewer bits, which:

    - **Reduces file size**: 4-bit = ~4× smaller than BF16
    - **Reduces VRAM usage**: fits models that wouldn't otherwise fit
    - **Increases throughput**: more weights fit in cache per cycle
    - **Costs quality**: more compression = more rounding = slightly worse outputs

    The sweet spot for most hardware is **4-bit**, which delivers near-BF16 quality at a quarter of the memory.

    ---

    ## Quant Name Reference

    GGUF quantization names follow a predictable pattern. Once you know it, any quant name is readable.

    ### Bit depth (first number)

    | Prefix | Bits per weight (avg) | File size vs BF16 | Quality vs BF16 |
    |--------|----------------------|-------------------|-----------------|
    | `Q2`   | ~2.6 bpw | ~16% | Noticeably degraded — avoid for reasoning tasks |
    | `Q3`   | ~3.4 bpw | ~21% | Usable floor; good for memory-tight setups |
    | `Q4`   | ~4.6 bpw | ~28% | **Sweet spot** — near-identical quality for most tasks |
    | `Q5`   | ~5.5 bpw | ~34% | Marginally better than Q4; rarely worth the extra VRAM |
    | `Q6`   | ~6.6 bpw | ~41% | Excellent; barely distinguishable from BF16 |
    | `Q8`   | ~8.5 bpw | ~53% | Near-lossless; use when you have the VRAM |
    | `BF16` | 16 bpw | 100% | Full precision; requires GPU with enough VRAM |

    ### Suffix: block strategy

    | Suffix | Meaning |
    |--------|---------|
    | `_K_S` | K-quant, small blocks — fewer bits in important layers |
    | `_K_M` | K-quant, medium — balanced across layers |
    | `_K_L` | K-quant, large — more bits in critical layers |
    | `_K_XL` | K-quant, extra large — most bits concentrated in attention/output layers |

    K-quants allocate bits non-uniformly across a block of weights, preserving more precision where it matters most. `Q4_K_M` is the standard recommendation for 16 GB VRAM.

    ### IQ variants (importance quantization)

    `IQ` quants use **importance matrices** to decide which weights to preserve most precisely. They often deliver better quality per bit than standard K-quants at the same bit depth.

    | Name | Effective bpw | Notes |
    |------|--------------|-------|
    | `IQ2_XXS` | ~2.1 | Extremely compressed; usable only for very large models |
    | `IQ3_XXS` | ~3.1 | Best choice when you need <13 GB VRAM |
    | `IQ3_XS` | ~3.3 | Slightly better than IQ3_XXS |
    | `IQ4_XS` | ~4.2 | Better quality-per-bit than Q4_K_M; worth trying |
    | `IQ4_NL` | ~4.5 | Non-linear importance; good alternative to Q4_K_M |

    ---

    ## Popular Variant Sources

    Not all GGUF uploads are equal. These are the most trusted sources.

    ### Unsloth Dynamic GGUF (recommended)

    [Unsloth](https://huggingface.co/unsloth) produces **Dynamic 2.0** quants that re-calibrate block importance using the model's actual activation patterns. Compared to standard quants of the same name:

    - Less quality loss at the same bit depth
    - Better reasoning and coding benchmarks, especially at Q3/Q4
    - Frequently the first to have new models available
    - Use their `UD-Q4_K_XL` as your default 4-bit choice (higher quality than `Q4_K_M`)

    ```bash
    # Download Unsloth Qwen3.6-27B 4-bit
    hf download unsloth/Qwen3.6-27B-GGUF \
      --include "Qwen3.6-27B-Q4_K_M.gguf" \
      --local-dir ./models/qwen3.6-27b
    ```

    ### bartowski

    [bartowski](https://huggingface.co/bartowski) produces high-quality standard K-quants and IQ variants. Well-organized repos with consistent naming. Good alternative to Unsloth when Unsloth hasn't published yet.

    ### lmstudio-community

    [lmstudio-community](https://huggingface.co/lmstudio-community) provides quants optimized for LM Studio, tested to load cleanly in the app. Useful if you're primarily a LM Studio user and want pre-validated files.

    ### TheBloke (legacy)

    [TheBloke](https://huggingface.co/TheBloke) was the dominant GGUF publisher for two years but is no longer actively updated. Files from 2023–2024 are fine but you'll find newer models only from the sources above.

    ---

    ## MLX Variants (Apple Silicon Only)

    For Apple Silicon, the native format is **MLX** — Apple's machine learning framework that uses unified memory (shared CPU/GPU/NPU). MLX variants are stored as safetensors shards, not GGUF.

    | Source | Notes |
    |--------|-------|
    | `mlx-community` | Community org on HuggingFace; primary source for MLX quants |
    | Unsloth MLX | `unsloth/Model-UD-MLX-4bit` — higher quality than standard mlx-community quants |

    ```bash
    # Install mlx-lm runtime
    uv venv .venv && source .venv/bin/activate
    uv pip install mlx-lm

    # Run a model (downloads on first run)
    mlx_lm.generate --model mlx-community/Qwen3.6-27B-4bit --max-tokens 4096
    ```

    MLX uses unified memory, so a 64 GB M3 Max can run a 55 GB BF16 model with ease. There is no VRAM limit separate from system RAM.

    ---

    ## How to Pick a Quant

    **By available VRAM (GPU inference):**

    | VRAM | Quant for 27B | Quant for 35B MoE |
    |------|--------------|-------------------|
    | 10 GB | IQ3_XXS (~12 GB with offload) | — |
    | 12 GB | Q3_K_M (with some CPU offload) | — |
    | 16 GB | **Q4_K_M** ← default | Q3 with offload |
    | 24 GB | Q6_K | **Q4_K_XL** ← default |
    | 32 GB | Q8_0 | Q6_K |
    | 48+ GB | BF16 (if available) | Q8_0 |

    **By Apple Silicon unified memory:**

    | RAM | Recommendation |
    |-----|---------------|
    | 16 GB | Q4_K_M (4-bit MLX) |
    | 32 GB | Q6_K or 8-bit MLX |
    | 48 GB | 8-bit MLX or small BF16 |
    | 64 GB+ | BF16 |

    **General rules:**
    - Start at **Q4_K_M** or **UD-Q4_K_XL** — this is where quality/size is best balanced
    - Go down to Q3/IQ3 only if you need to fit the model
    - Go up to Q6/Q8 if you have the headroom and want slightly better reasoning
    - `IQ4_XS` and `IQ3_XXS` from Unsloth are often better than their K-quant counterparts at the same size

    ---

    ## llama.cpp: Direct HuggingFace Streaming

    llama.cpp can stream GGUF directly from HuggingFace, caching on first use. No separate download step:

    ```bash
    export LLAMA_CACHE="./models"

    # Stream and cache on first run; subsequent runs use cache
    llama-server -hf unsloth/Qwen3.6-27B-GGUF:Q4_K_M --port 8001
    ```

    This is equivalent to downloading first and running locally — the file is cached to `LLAMA_CACHE` and reused.

    ---

    ## Checking a Model's Actual bpw

    To inspect what quantization a GGUF file actually uses:

    ```bash
    # llama.cpp ships with gguf-dump
    ./gguf-dump model.gguf | grep quantization
    ```

    Or load it in LM Studio — the model info panel shows bits per weight for each tensor group.
    