#!/usr/bin/env python3
"""
Generate OmniGraffle-style blueprint PNGs for all 9 local-llm-guides diagrams
using the Gemini image generation API (nano-banana).
"""

import asyncio
import base64
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types

REPO = Path(__file__).parent
DOT_DIR = REPO / "diagrams"
OUT_DIR = REPO / "diagrams" / "blueprint"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DIAGRAMS = [
    ("backend_selector.dot",       "backend_selector_blueprint.png"),
    ("hardware_selector.dot",      "hardware_selector_blueprint.png"),
    ("vllm_decision.dot",          "vllm_decision_blueprint.png"),
    ("rocm_backend.dot",           "rocm_backend_blueprint.png"),
    ("mlx_path_selector.dot",      "mlx_path_selector_blueprint.png"),
    ("gemma4_variant.dot",         "gemma4_variant_blueprint.png"),
    ("qwen35_variant.dot",         "qwen35_variant_blueprint.png"),
    ("agent_model_selector.dot",   "agent_model_selector_blueprint.png"),
    ("local_cloud_fallback.dot",   "local_cloud_fallback_blueprint.png"),
]

# ── OmniGraffle / Apple-style aesthetic ──────────────────────────────────────
STYLE = """
AESTHETIC: OmniGraffle 7 / Apple macOS diagram style — crisp, professional,
presentation-ready. As if drawn with OmniGraffle's default "Ethan" template.

VISUAL RULES (must follow exactly):
- Background: solid white #FFFFFF, no texture, generous padding
- Canvas: 1200×900px, portrait or landscape as needed for the flow
- Process / result nodes: rounded rectangles, corner-radius 8pt
  · Default fill: soft ice blue #E8F1FB, border #7AADD4 1.5pt
  · High-priority result fill: light mint #E6F5EE, border #5BAD85
  · Warning result fill: soft amber #FFF3E0, border #E8A838
  · Error result fill: soft rose #FDECEA, border #E57373
- Decision nodes: diamond shape, pale yellow fill #FFF9E6, border #C8A84B 1.5pt
- Start / end nodes: rounded pill / stadium shape, slate blue fill #5B8DB8,
  white text, border #3D6E99 1.5pt
- Connectors: orthogonal right-angle routing, 1.5pt dark gray #4A4A4A lines,
  small solid filled arrowheads, edge labels in 10pt gray #666666
- Typography: Helvetica Neue (or SF Pro), 12pt dark charcoal #2C2C2C for node
  labels; 10pt gray #666666 for edge labels; no bold except pill start/end nodes
- Drop shadows on nodes: 2pt offset, 8% black opacity — subtle, not heavy
- NO gradients, NO textures, NO glow, NO neon, NO dark backgrounds
- Generous whitespace between nodes — OmniGraffle-style breathing room
- Overall mood: macOS-native, calm, authoritative, boardroom-safe
"""

PROMPT_TEMPLATE = """
Render the following flowchart as a high-resolution diagram image in OmniGraffle style.

{style}

DIAGRAM TOPOLOGY (Graphviz DOT source — preserve every node and edge exactly):
{dot_source}

RENDERING INSTRUCTIONS:
- Reproduce every node label exactly as written in the DOT source
- Reproduce every edge and edge label exactly — do not add or remove connections
- Use the node shapes specified: ellipse → pill/stadium, diamond → diamond,
  box → rounded rectangle
- Apply the color mapping from the DOT fillcolor hints:
  · #0d3321 (dark green) → use light mint fill #E6F5EE, green border #5BAD85
  · #1a1a2e (dark blue) → use ice blue fill #E8F1FB, blue border #7AADD4
  · #2d0d4e (dark purple) → use light lavender fill #F0EBF8, purple border #9B77C8
  · #2d0d0d (dark red) → use soft rose fill #FDECEA, red border #E57373
  · #2d2100 (dark amber) → use soft amber fill #FFF3E0, orange border #E8A838
  · #2d1a00 (dark brown) → use pale peach fill #FFF0E6, orange border #E67E22
  · no fillcolor specified → default ice blue #E8F1FB
- Layout direction: top-to-bottom
- Output: single image, no title bar, no legend, no watermark
- Quality: sharp, clean edges, pixel-perfect text, publication-ready
"""


async def generate_diagram(client, dot_name: str, out_name: str) -> bool:
    dot_path = DOT_DIR / dot_name
    out_path = OUT_DIR / out_name

    dot_source = dot_path.read_text(encoding="utf-8")
    prompt = PROMPT_TEMPLATE.format(style=STYLE, dot_source=dot_source)

    print(f"  Generating {out_name}...")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
        )

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                img_data = part.inline_data.data
                # data may be bytes or base64 string
                if isinstance(img_data, str):
                    img_data = base64.b64decode(img_data)
                out_path.write_bytes(img_data)
                print(f"  ✅ Saved → {out_path.relative_to(REPO)}")
                return True

        print(f"  ❌ No image in response for {dot_name}")
        # Print any text for debugging
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                print(f"     Model said: {part.text[:200]}")
        return False

    except Exception as e:
        print(f"  ❌ Error generating {dot_name}: {e}")
        return False


async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print(f"Generating {len(DIAGRAMS)} OmniGraffle-style blueprint PNGs...\n")

    results = []
    # Run one at a time to avoid rate limits
    for dot_name, out_name in DIAGRAMS:
        ok = await generate_diagram(client, dot_name, out_name)
        results.append((out_name, ok))
        await asyncio.sleep(2)  # brief pause between calls

    print("\n── Summary ──────────────────────────────")
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status}  {name}")

    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(DIAGRAMS)} generated successfully")


if __name__ == "__main__":
    asyncio.run(main())
