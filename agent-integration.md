# Agent Integration Guide

This guide walks you through connecting Amplifier agents to a local LLM — from starting your server to making your first request. Use the selectors above to filter commands for your setup.

---

## Quick Reference: Endpoint URLs

| Backend | Default URL | Model name |
|---------|-------------|-----------|
| llama-server | `http://localhost:8001/v1` | `--alias` value at server start |
| Ollama | `http://localhost:11434/v1` | exact name from `ollama list` |
| vLLM | `http://localhost:8000/v1` | HuggingFace model ID |
| LM Studio | `http://localhost:1234/v1` | shown in Developer tab |

---

## Step 1: Start Your Local Server

Pick a backend below and run the command. Leave this running — the following steps connect to it.

<!-- when:backend=llamacpp -->

**Qwen3.6-27B** — flagship coding model, fits 16 GB VRAM (streams the ~17 GB Q4 file on first run):

```bash
llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:Q4_K_M \
  --alias "qwen3.6-27b" \
  --ctx-size 65536 \
  --n-gpu-layers 999 \
  --cache-ram 4096 \
  --flash-attn \
  --temp 0.6 \
  --top-p 0.95 \
  --top-k 20 \
  --min-p 0.0 \
  --parallel 4 \
  --cont-batching \
  --jinja \
  --reasoning on \
  --chat-template-kwargs '{"enable_thinking":true}' \
  --port 8001
```

**Qwen3.6-35B-A3B** — MoE model if you have 24 GB VRAM and need vision:

```bash
./llama.cpp/llama-server \
  --model ./models/qwen3.6-35b/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
  --mmproj ./models/qwen3.6-35b/mmproj-F16.gguf \
  --alias "qwen3.6" \
  --ctx-size 32768 \
  --n-gpu-layers 999 \
  --flash-attn \
  --parallel 4 \
  --cont-batching \
  --chat-template-kwargs '{"enable_thinking":true}' \
  --port 8001
```

<!-- /when -->

<!-- when:backend=ollama -->

```bash
ollama serve &
ollama pull qwen3.6:27b
# Server at http://localhost:11434/v1  model: "qwen3.6:27b"
```

For the MoE model: `ollama pull qwen3.6:35b-a3b`

<!-- /when -->

<!-- when:backend=vllm -->

**Qwen3.6-27B** on a single A100/H100/MI300X:

```bash
vllm serve Qwen/Qwen3.6-27B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 65536 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --host 0.0.0.0
```

Multi-GPU for 262K context:

```bash
vllm serve Qwen/Qwen3.6-27B \
  --port 8000 \
  --tensor-parallel-size 4 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

<!-- /when -->

<!-- when:backend=lmstudio -->

1. Open LM Studio → Browse → search `Qwen3.6-27B` → Download the Q4_K_M GGUF
2. Go to the **Developer** tab → Load Model → click **Start Server**
3. Server starts at `http://localhost:1234/v1` — the model name is shown in the tab header

<!-- /when -->

Confirm the server is up:

```bash
curl http://localhost:8001/v1/models   # or :11434/v1/models, :8000/v1/models, :1234/v1/models
```

---

## Step 2: Configure Amplifier

The `provider-chat-completions` module ships pre-installed with `amplifier-app-cli`. Run the interactive wizard:

```bash
amplifier provider manage
```

Select **"OpenAI-Compatible (self-hosted)"**, then enter:

<!-- when:backend=llamacpp -->

| Prompt | Value |
|--------|-------|
| Base URL | `http://localhost:8001/v1` |
| Model name | `qwen3.6-27b` (or whatever you passed to `--alias`) |
| API key | `not-needed` |

<!-- /when -->

<!-- when:backend=ollama -->

| Prompt | Value |
|--------|-------|
| Base URL | `http://localhost:11434/v1` |
| Model name | `qwen3.6:27b` (exact name from `ollama list`) |
| API key | `not-needed` |

<!-- /when -->

<!-- when:backend=vllm -->

| Prompt | Value |
|--------|-------|
| Base URL | `http://localhost:8000/v1` |
| Model name | `Qwen/Qwen3.6-27B` (exact HuggingFace ID matching your `--model` arg) |
| API key | `not-needed` (or your `--api-key` value if set) |

<!-- /when -->

<!-- when:backend=lmstudio -->

| Prompt | Value |
|--------|-------|
| Base URL | `http://localhost:1234/v1` |
| Model name | model name shown in the Developer tab |
| API key | `not-needed` |

<!-- /when -->

After the wizard completes, your `~/.amplifier/settings.yaml` gets a new provider block and `~/.amplifier/keys.env` gets the base URL. Verify:

```bash
amplifier provider current
```

### Route specific tasks to the local model

Add routing overrides to `~/.amplifier/settings.yaml`:

```yaml
routing:
  matrix: balanced
  overrides:
    coding:
      - provider: chat-completions
        model: qwen3.6-27b   # or your vLLM model ID / ollama model name
    fast:
      - provider: chat-completions
        model: qwen3.6-27b
      - base               # fall back to balanced matrix if local server is down
```

`base` appends the matrix's original candidates after your local model. Without it, only your local model is tried for that role.

---

## Step 3: Verify the Connection

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6-27b",
    "messages": [{"role": "user", "content": "Reply with: connection OK"}],
    "max_tokens": 20
  }'
```

You should see a response with `"content": "connection OK"` (or similar). If not, check that the server from Step 1 is still running.

---

## Step 4: Make Your First Agentic Request

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",   # match your backend
    api_key="not-needed",
)

# Basic chat
response = client.chat.completions.create(
    model="qwen3.6-27b",                   # match your --alias or model name
    messages=[
        {"role": "system", "content": "You are a senior software engineer."},
        {"role": "user", "content": "Write a Python function that checks if a number is prime."},
    ],
    max_tokens=2048,
    temperature=0.6,
)
print(response.choices[0].message.content)
```

With thinking mode (Qwen3.x — access the reasoning trace):

```python
response = client.chat.completions.create(
    model="qwen3.6-27b",
    messages=[{"role": "user", "content": "Find the bug: def fib(n): return fib(n-1)+fib(n-2)"}],
    max_tokens=8192,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
reasoning = getattr(response.choices[0].message, "reasoning_content", None)
if reasoning:
    print("=== Thinking ===")
    print(reasoning)
print("=== Answer ===")
print(response.choices[0].message.content)
```

---

## Reference: Streaming

```python
stream = client.chat.completions.create(
    model="qwen3.6-27b",
    messages=[{"role": "user", "content": "Write a REST API in FastAPI."}],
    max_tokens=16384,
    temperature=0.6,
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## Reference: Tool Calling (Agentic Loop)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return stdout",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    }
]

messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Check if there are any Python syntax errors in the src/ directory."},
]

response = client.chat.completions.create(
    model="qwen3.6-27b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    max_tokens=4096,
)

while response.choices[0].finish_reason == "tool_calls":
    import json, subprocess
    messages.append(response.choices[0].message)
    for tc in response.choices[0].message.tool_calls:
        args = json.loads(tc.function.arguments)
        result = subprocess.run(args["command"], shell=True, capture_output=True, text=True)
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result.stdout + result.stderr,
        })
    response = client.chat.completions.create(
        model="qwen3.6-27b", messages=messages, tools=tools,
        tool_choice="auto", max_tokens=4096,
    )

print(response.choices[0].message.content)
```

---

## Reference: Vision (Multimodal)

Both Gemma 4 and Qwen3.5/3.6 support image input when served with an mmproj:

```python
import base64

def analyze_image(image_path: str, question: str, model: str = "qwen3.6-27b") -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": question},
            ],
        }],
        max_tokens=2048,
        temperature=1.0,
    )
    return response.choices[0].message.content

result = analyze_image("screenshot.png", "Identify all UI elements and describe their purpose.")
print(result)
```

---

## Reference: Background Server Process

```bash
# Start server in background (persists after shell exit)
nohup llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:Q4_K_M \
  --alias "qwen3.6-27b" \
  --ctx-size 32768 \
  --n-gpu-layers 999 \
  --parallel 4 --cont-batching \
  --jinja --reasoning on \
  --chat-template-kwargs '{"enable_thinking":true}' \
  --port 8001 \
  > ./llama-server.log 2>&1 &
echo "Server PID: $!"
```

Health check:

```bash
curl -s http://localhost:8001/health      # {"status":"ok"}
curl -s http://localhost:8001/v1/models | python3 -m json.tool
```

---

## Reference: Model Selection by Task

![Agent Model Selector — Decision Schematic](diagrams/rendered/agent_model_selector.png)

| Task | Best Model | Thinking | Temperature |
|------|-----------|----------|-------------|
| Code generation (precise) | **Qwen3.6-27B** or 35B-A3B | On | 0.6 |
| Agentic coding, 16 GB VRAM | **Qwen3.6-27B** | On | 0.6 |
| General reasoning | Gemma 4 26B-A4B or 31B | On | 1.0 |
| Multi-step planning | Qwen3.6-27B or Gemma 4 31B | On | 1.0 |
| Document / image analysis | Gemma 4 26B-A4B | Optional | 1.0 |
| Fast, high-volume | Gemma 4 E4B | Off | 1.0 |
| Edge / offline | Gemma 4 E2B | Off | 1.0 |
| Structured JSON extraction | Any | Off | 0.0–0.3 |

---

## Reference: Context Length Planning

| Backend | Practical max | Notes |
|---------|-------------|-------|
| llama-server | 128K (with flash-attn + q8 KV) | Each slot costs `ctx × layers × d_model × 2 × dtype` |
| Ollama | 32K default; up to 128K via Modelfile | Increase `num_ctx` carefully |
| vLLM | Up to 262K (Qwen3.x), 256K (Gemma 4) | Reduce `--max-model-len` to free KV cache for batching |
| LM Studio | Up to model max; set in Developer tab | Higher context = slower TTFT |

For agentic coding, 32K is usually sufficient. For document analysis, 64K–128K is appropriate.

---

## Reference: Local → Cloud Fallback Pattern

![Local / Cloud Fallback — Flow Schematic](diagrams/rendered/local_cloud_fallback.png)

```python
import os
from openai import OpenAI

LOCAL_URL   = "http://localhost:8001/v1"
LOCAL_MODEL = "qwen3.6-27b"
CLOUD_MODEL = "gpt-4o"

def get_client():
    try:
        c = OpenAI(base_url=LOCAL_URL, api_key="not-needed")
        c.models.list()   # quick probe
        return c, LOCAL_MODEL
    except Exception:
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), CLOUD_MODEL

client, model = get_client()
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello"}],
)
print(f"Using: {model}")
print(response.choices[0].message.content)
```

---

## Reference: Server Health Check

```python
import httpx
from openai import OpenAI

def check_local_llm(base_url: str = "http://localhost:8001") -> bool:
    try:
        r = httpx.get(f"{base_url}/health", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False

def get_models(base_url: str = "http://localhost:8001") -> list[str]:
    c = OpenAI(base_url=f"{base_url}/v1", api_key="not-needed")
    return [m.id for m in c.models.list().data]

if check_local_llm():
    print("Local LLM is up:", get_models())
else:
    print("Local LLM not running — falling back to cloud")
```
