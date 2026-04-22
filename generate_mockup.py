#!/usr/bin/env python3
"""
generate_mockup.py — Regenerate mockup.html from diagrams/rendered/*.png
─────────────────────────────────────────────────────────────────────────
Usage:
    python3 generate_mockup.py          # writes mockup.html
    make                                # same, via Makefile
"""

from pathlib import Path

# ── Diagram metadata ──────────────────────────────────────────────────────────
# Order controls card sequence in the gallery.
# Keys must match the PNG stem in diagrams/rendered/.

DIAGRAMS = [
    {"slug": "backend_selector",     "name": "Backend Selector",       "category": "BACKEND"},
    {"slug": "vllm_decision",        "name": "vLLM vs llama.cpp",      "category": "BACKEND"},
    {"slug": "hardware_selector",    "name": "Hardware Selector",       "category": "HARDWARE"},
    {"slug": "rocm_backend",         "name": "AMD ROCm Support",        "category": "HARDWARE"},
    {"slug": "mlx_path_selector",    "name": "Apple Silicon MLX",       "category": "HARDWARE"},
    {"slug": "agent_model_selector", "name": "Agent Model Selector",    "category": "MODELS"},
    {"slug": "gemma4_variant",       "name": "Gemma 4 Variants",        "category": "MODELS"},
    {"slug": "qwen35_variant",       "name": "Qwen3.5 Variants",        "category": "MODELS"},
    {"slug": "local_cloud_fallback", "name": "Local \u2192 Cloud Fallback", "category": "ROUTING"},
]

RENDERED_DIR = Path("diagrams/rendered")
OUT_FILE     = Path("mockup.html")

# ── Validate ──────────────────────────────────────────────────────────────────

missing = [d for d in DIAGRAMS if not (RENDERED_DIR / f"{d['slug']}.png").exists()]
if missing:
    print("  warn  missing PNGs (run `make diagrams` first):")
    for d in missing:
        print(f"        {RENDERED_DIR / d['slug']}.png")

diagrams = [d for d in DIAGRAMS if (RENDERED_DIR / f"{d['slug']}.png").exists()]

# ── Build card HTML ───────────────────────────────────────────────────────────

def card(d: dict) -> str:
    src = f"diagrams/rendered/{d['slug']}.png"
    return f"""\
        <article class="diagram-card" tabindex="0" role="button" aria-label="View {d['name']}"
                 data-src="{src}" data-name="{d['name']}">
          <div class="card-tag">
            <span class="card-category">{d['category']}</span>
          </div>
          <div class="card-img-wrap">
            <img src="{src}" alt="{d['name']} decision graph" loading="lazy">
          </div>
          <div class="card-foot">
            <span class="card-name">{d['name']}</span>
            <span class="card-arrow" aria-hidden="true">&rarr;</span>
          </div>
        </article>"""

cards_html = "\n".join(card(d) for d in diagrams)

# ── Stats ─────────────────────────────────────────────────────────────────────

categories = sorted({d["category"] for d in diagrams})
n_diagrams  = len(diagrams)
n_cats      = len(categories)

# ── HTML template ─────────────────────────────────────────────────────────────

HTML = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Local LLM Guides \u2014 Decision Graphs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    /* \u2500\u2500\u2500 Reset \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    /* \u2500\u2500\u2500 Tokens \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    :root {{
      --bg:         #ffffff;
      --surface:    #fafafa;
      --surface-2:  #f4f4f5;
      --border:     #e4e4e7;
      --border-mid: #d4d4d8;
      --muted:      #d4d4d8;
      --text:       #09090b;
      --text-mid:   #52525b;
      --text-dim:   #a1a1aa;
      --accent:     #2563eb;
      --ease:       cubic-bezier(0.16, 1, 0.3, 1);
      --t:          200ms;
    }}

    /* \u2500\u2500\u2500 Base \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    html {{ font-size: 14px; scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }}

    /* \u2500\u2500\u2500 Layout \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 0 40px; }}

    /* \u2500\u2500\u2500 Header \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .site-header {{ border-bottom: 1px solid var(--border); padding: 18px 0; }}
    .header-row  {{ display: flex; align-items: center; justify-content: space-between; }}
    .header-identity {{ display: flex; align-items: center; gap: 14px; }}

    .logo-mark {{
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 2px; width: 28px; height: 28px; flex-shrink: 0;
    }}
    .logo-mark i {{ display: block; border-radius: 4px; }}
    .logo-mark i:nth-child(1) {{ background: var(--text); }}
    .logo-mark i:nth-child(2) {{ background: var(--accent); }}
    .logo-mark i:nth-child(3) {{ background: var(--accent); }}
    .logo-mark i:nth-child(4) {{ background: var(--text); }}

    .header-text {{ display: flex; flex-direction: column; gap: 2px; }}
    .site-name {{
      font-size: 0.8125rem; font-weight: 600; letter-spacing: 0.14em;
      color: var(--text); text-transform: uppercase; line-height: 1;
    }}
    .site-sub {{
      font-size: 0.62rem; font-weight: 700; letter-spacing: 0.16em;
      color: var(--text-dim); text-transform: uppercase; line-height: 1;
    }}
    .header-tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.62rem; font-weight: 500; letter-spacing: 0.08em;
      color: var(--text-dim); border: 1px solid var(--border);
      padding: 5px 9px; border-radius: 3px; text-transform: uppercase;
    }}

    /* \u2500\u2500\u2500 Main \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    main {{ padding: 56px 0 88px; }}

    /* \u2500\u2500\u2500 Section head \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .section-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }}
    .section-label {{
      font-size: 0.62rem; font-weight: 700; letter-spacing: 0.16em;
      color: var(--text-dim); text-transform: uppercase; white-space: nowrap;
      padding-left: 9px; border-left: 2px solid var(--accent); line-height: 1;
    }}
    .section-rule {{ flex: 1; height: 1px; background: var(--border); }}

    /* \u2500\u2500\u2500 Grid \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .diagram-grid {{
      display: grid; grid-template-columns: repeat(3, 1fr);
      gap: 1px; background: var(--border); border: 1px solid var(--border);
    }}

    /* \u2500\u2500\u2500 Card \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .diagram-card {{
      background: var(--surface); cursor: pointer;
      display: flex; flex-direction: column;
      transition: background var(--t) var(--ease); outline: none;
    }}
    .diagram-card:hover, .diagram-card:focus-visible {{ background: var(--surface-2); }}
    .diagram-card:focus-visible {{ box-shadow: inset 0 0 0 2px var(--accent); }}

    .card-tag {{ padding: 9px 13px; border-bottom: 1px solid var(--border); }}
    .card-category {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.59rem; font-weight: 700; letter-spacing: 0.18em;
      color: var(--text-dim); text-transform: uppercase;
    }}

    .card-img-wrap {{
      background: #fff; border-bottom: 1px solid var(--border);
      overflow: hidden; aspect-ratio: 3 / 4; position: relative;
    }}
    .card-img-wrap img {{
      position: absolute; inset: 0; width: 100%; height: 100%;
      object-fit: contain; padding: 10px; display: block;
      transition: opacity var(--t) var(--ease), transform var(--t) var(--ease);
    }}
    .diagram-card:hover .card-img-wrap img {{ opacity: 0.90; transform: scale(1.012); }}

    .card-foot {{
      padding: 11px 13px; display: flex; align-items: center;
      justify-content: space-between; gap: 8px; margin-top: auto;
    }}
    .card-name {{ font-size: 0.8125rem; font-weight: 500; letter-spacing: -0.01em; color: var(--text); }}
    .card-arrow {{
      font-size: 0.875rem; color: var(--text-dim); flex-shrink: 0;
      transition: color var(--t) var(--ease), transform var(--t) var(--ease);
    }}
    .diagram-card:hover .card-arrow, .diagram-card:focus-visible .card-arrow {{
      color: var(--accent); transform: translateX(3px);
    }}

    /* \u2500\u2500\u2500 About \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .about-section {{ margin-top: 72px; }}
    .about-body {{
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 1px; background: var(--border); border: 1px solid var(--border);
    }}
    .about-left  {{ background: var(--surface); padding: 32px 36px; }}
    .about-right {{ background: var(--surface); padding: 32px 36px; }}
    .about-desc  {{ font-size: 0.9375rem; color: var(--text-mid); line-height: 1.75; max-width: 400px; }}

    .stat-block {{ display: flex; flex-direction: column; gap: 14px; }}
    .stat-row   {{ display: flex; align-items: baseline; }}
    .stat-num   {{
      font-family: 'JetBrains Mono', monospace; font-size: 1rem;
      font-weight: 700; color: var(--text); min-width: 28px; letter-spacing: -0.02em;
    }}
    .stat-sep   {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--text-dim); margin-right: 12px; }}
    .stat-label {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--text-mid); }}
    .stat-note  {{ font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--text-dim); margin-left: 10px; }}

    /* \u2500\u2500\u2500 Footer \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .site-footer {{ border-top: 1px solid var(--border); padding: 18px 0; }}
    .footer-row  {{ display: flex; align-items: center; justify-content: space-between; }}
    .footer-name {{ font-size: 0.62rem; font-weight: 700; letter-spacing: 0.16em; color: var(--text-dim); text-transform: uppercase; }}
    .footer-right {{ display: flex; align-items: center; gap: 14px; }}
    .footer-year {{ font-size: 0.75rem; color: var(--text-dim); }}
    .footer-gh   {{ color: var(--text-dim); display: flex; align-items: center; text-decoration: none; transition: color var(--t) var(--ease); }}
    .footer-gh:hover {{ color: var(--text-mid); }}

    /* \u2500\u2500\u2500 Lightbox \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    .lightbox {{
      position: fixed; inset: 0; background: rgba(0,0,0,0.92);
      display: flex; align-items: center; justify-content: center;
      z-index: 9999; padding: 40px; cursor: zoom-out;
      opacity: 0; pointer-events: none; transition: opacity var(--t) var(--ease);
    }}
    .lightbox.is-open {{ opacity: 1; pointer-events: all; }}
    .lightbox-inner {{
      position: relative; cursor: default;
      display: flex; flex-direction: column; align-items: flex-start;
      transform: scale(0.97); transition: transform var(--t) var(--ease);
    }}
    .lightbox.is-open .lightbox-inner {{ transform: scale(1); }}
    .lightbox-img {{
      display: block; max-width: min(88vw, 1100px); max-height: 82vh;
      object-fit: contain; background: #fff;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.12), 0 24px 80px rgba(0,0,0,0.7);
    }}
    .lightbox-bar {{
      display: flex; align-items: center; justify-content: space-between;
      width: 100%; padding: 10px 0 0; gap: 16px;
    }}
    .lightbox-title {{ font-size: 0.75rem; font-weight: 500; color: rgba(255,255,255,0.6); letter-spacing: -0.01em; }}
    .lightbox-hint  {{ font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: rgba(255,255,255,0.3); letter-spacing: 0.08em; }}

    /* \u2500\u2500\u2500 Responsive \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
    @media (max-width: 1023px) {{ .diagram-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 639px) {{
      .wrap {{ padding: 0 20px; }}
      main  {{ padding: 40px 0 64px; }}
      .diagram-grid, .about-body {{ grid-template-columns: 1fr; }}
      .about-left, .about-right  {{ padding: 28px 24px; }}
      .lightbox {{ padding: 24px 16px; }}
      .lightbox-img {{ max-width: 100%; max-height: 75vh; }}
    }}
  </style>
</head>
<body>

  <header class="site-header">
    <div class="wrap">
      <div class="header-row">
        <div class="header-identity">
          <div class="logo-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <div class="header-text">
            <span class="site-name">Local LLM Guides</span>
            <span class="site-sub">Decision Graphs &middot; {n_diagrams} Diagrams</span>
          </div>
        </div>
        <div class="header-tag">Graphviz &middot; 2026</div>
      </div>
    </div>
  </header>

  <main>
    <div class="wrap">

      <div class="section-head">
        <span class="section-label">Decision Graphs</span>
        <span class="section-rule"></span>
      </div>

      <div class="diagram-grid">
{cards_html}
      </div>

      <section class="about-section" aria-label="About">
        <div class="section-head">
          <span class="section-label">About</span>
          <span class="section-rule"></span>
        </div>
        <div class="about-body">
          <div class="about-left">
            <p class="about-desc">
              Nine decision graphs for engineers choosing local LLM
              infrastructure. Pick a backend. Match hardware to models.
              Route traffic intelligently.
            </p>
          </div>
          <div class="about-right">
            <div class="stat-block">
              <div class="stat-row">
                <span class="stat-num">{n_diagrams}</span>
                <span class="stat-sep">&nbsp;&nbsp;</span>
                <span class="stat-label">diagrams</span>
              </div>
              <div class="stat-row">
                <span class="stat-num">{n_cats}</span>
                <span class="stat-sep">&nbsp;&nbsp;</span>
                <span class="stat-label">categories</span>
              </div>
              <div class="stat-row">
                <span class="stat-num">3</span>
                <span class="stat-sep">&nbsp;&nbsp;</span>
                <span class="stat-label">model families</span>
                <span class="stat-note">Qwen, Gemma, local stack</span>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-row">
        <span class="footer-name">Local LLM Guides</span>
        <div class="footer-right">
          <span class="footer-year">&copy; 2026</span>
          <a class="footer-gh" href="https://github.com/microsoft/local-llm-guides"
             target="_blank" rel="noopener noreferrer" aria-label="GitHub">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483
                       0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466
                       -.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832
                       .092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688
                       -.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844
                       a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651
                       .64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856
                       0 1.338-.012 2.419-.012 2.748 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017
                       C22 6.484 17.522 2 12 2Z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </footer>

  <div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Diagram viewer">
    <div class="lightbox-inner" id="lightbox-inner">
      <img class="lightbox-img" id="lightbox-img" src="" alt="">
      <div class="lightbox-bar">
        <span class="lightbox-title" id="lightbox-title"></span>
        <span class="lightbox-hint">ESC or click outside to close</span>
      </div>
    </div>
  </div>

  <script>
    'use strict';
    const lb      = document.getElementById('lightbox');
    const lbInner = document.getElementById('lightbox-inner');
    const lbImg   = document.getElementById('lightbox-img');
    const lbTitle = document.getElementById('lightbox-title');
    let prev = null;

    function open(src, name) {{
      prev = document.activeElement;
      lbImg.src = src; lbImg.alt = name;
      lbTitle.textContent = name;
      lb.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }}
    function close() {{
      lb.classList.remove('is-open');
      document.body.style.overflow = '';
      setTimeout(() => {{ lbImg.src = ''; }}, 220);
      if (prev) prev.focus({{ preventScroll: true }});
    }}

    document.querySelectorAll('.diagram-card').forEach(card => {{
      const src  = card.dataset.src;
      const name = card.dataset.name;
      card.addEventListener('click', () => open(src, name));
      card.addEventListener('keydown', e => {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); open(src, name); }}
      }});
    }});

    lb.addEventListener('click', e => {{ if (!lbInner.contains(e.target)) close(); }});
    document.addEventListener('keydown', e => {{ if (e.key === 'Escape' && lb.classList.contains('is-open')) close(); }});
    lbInner.addEventListener('click', e => e.stopPropagation());
  </script>

</body>
</html>"""

# ── Write ─────────────────────────────────────────────────────────────────────

OUT_FILE.write_text(HTML, encoding="utf-8")
