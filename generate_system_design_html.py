#!/usr/bin/env python3
"""Generate self-contained, interactive HTML workbooks from System Design README.md files.
"""
import os
import re
from pathlib import Path

BASE_DIR = Path("/Users/sailikhithkanuparthi/Downloads/career/interview-prep/interview-prep-notes/SystemDesign")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>System Design: {title} — Study Workbook</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<!-- Mermaid.js for Diagrams -->
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
  startOnLoad: true,
  theme: 'neutral',
  themeVariables: {{
    background: '#ffffff',
    primaryColor: '#f3f4f6',
    primaryTextColor: '#1f2937',
    lineColor: '#2563eb',
    primaryBorderColor: '#e5e7eb',
    nodeBorder: '#d1d5db',
    actorBorder: '#d1d5db',
    actorBkg: '#f9fafb',
    signalColor: '#2563eb',
    signalTextColor: '#1e3a8a'
  }}
}});
</script>
<!-- MathJax -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>
tailwind.config = {{
  theme: {{
    extend: {{
      fontFamily: {{ sans: ['Inter','sans-serif'], mono: ['JetBrains Mono','monospace'] }},
      colors: {{
        brand: {{ 50:'#eff6ff', 100:'#dbeafe', 500:'#3b82f6', 600:'#2563eb', 700:'#1d4ed8', 900:'#1e3a8a' }}
      }}
    }}
  }}
}}
</script>
<style>
body {{ font-family:'Inter',sans-serif; }}
.code {{ font-family:'JetBrains Mono',monospace; }}
.gradient-text {{ background:linear-gradient(135deg,#2563eb,#7c3aed,#db2777); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
.hero-glow {{ background:radial-gradient(ellipse 70% 60% at 50% 0%,rgba(37,99,235,0.08) 0%,transparent 100%); }}
details > summary {{ list-style:none; cursor:pointer; }}
details > summary::-webkit-details-marker {{ display:none; }}
</style>
</head>
<body class="bg-gray-50 text-gray-900 antialiased min-h-screen relative overflow-x-hidden">

<!-- Ambient Glow -->
<div class="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[350px] hero-glow pointer-events-none"></div>

<!-- HEADER -->
<header class="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-gray-200">
  <div class="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-black text-sm shadow-md shadow-blue-500/20">SD</div>
      <div>
        <span class="font-extrabold text-gray-900 tracking-tight text-base">{title}</span>
        <span class="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">System Design Workbook</span>
      </div>
    </div>
    <a href="../README.md" class="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors">&larr; Back to System Design Hub</a>
  </div>
</header>

<!-- HERO -->
<div class="border-b border-gray-200 bg-white hero-glow relative">
  <div class="max-w-5xl mx-auto px-6 py-12">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Architectural Study Guide</span>
      <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
      <span class="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded">High Scale &bull; Distributed Systems</span>
    </div>
    <h1 class="text-3xl sm:text-4xl font-black tracking-tight mb-4">
      <span class="gradient-text">{title}</span>
    </h1>
    <p class="text-gray-600 text-base max-w-3xl leading-relaxed">
      Comprehensive architectural deep-dive covering high-level data flow, data models, edge case failure modes, scaling strategies, and interview trade-off defenses.
    </p>
  </div>
</div>

<!-- CONTENT MAIN -->
<main class="max-w-5xl mx-auto px-6 py-10 space-y-8">
  <div class="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm prose prose-blue max-w-none space-y-6">
    {body_html}
  </div>
</main>

<footer class="border-t border-gray-200 bg-white py-8 text-center text-xs text-gray-500">
  <p>System Design Interactive Study Suite &bull; AntiGravity IDE</p>
</footer>
</body>
</html>
"""


def convert_markdown_to_html(md_text: str) -> str:
    """Simple converter for markdown sections into formatted HTML."""
    lines = md_text.split('\n')
    html_out = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith('```'):
            if in_code_block:
                code_content = '\n'.join(code_lines)
                if code_lang == 'mermaid':
                    html_out.append(f'<div class="my-6 bg-white border border-gray-200 rounded-xl p-4"><div class="mermaid flex justify-center py-2">\n{code_content}\n</div></div>')
                else:
                    html_out.append(f'<div class="my-4 bg-gray-900 text-gray-100 rounded-xl p-4 text-xs font-mono overflow-x-auto"><pre><code>{code_content}</code></pre></div>')
                in_code_block = False
                code_lines = []
                code_lang = ""
            else:
                in_code_block = True
                code_lang = stripped[3:].strip().lower()
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Close lists if empty line or header
        if in_list and (not stripped or stripped.startswith('#')):
            html_out.append('</ul>')
            in_list = False

        if not stripped:
            continue

        # Headers
        if stripped.startswith('# '):
            html_out.append(f'<h1 class="text-2xl font-black text-gray-900 border-b border-gray-200 pb-3 mb-4 mt-6">{stripped[2:]}</h1>')
        elif stripped.startswith('## '):
            html_out.append(f'<h2 class="text-xl font-bold text-gray-900 border-b border-gray-100 pb-2 mb-3 mt-6 text-indigo-900">{stripped[3:]}</h2>')
        elif stripped.startswith('### '):
            html_out.append(f'<h3 class="text-base font-bold text-gray-800 mb-2 mt-4 text-blue-900">{stripped[4:]}</h3>')
        elif stripped.startswith('#### '):
            html_out.append(f'<h4 class="text-sm font-bold text-gray-800 mb-1 mt-3">{stripped[5:]}</h4>')
        # Bullets
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_out.append('<ul class="list-disc pl-5 space-y-1.5 text-xs sm:text-sm text-gray-700 my-2">')
                in_list = True
            content = stripped[2:]
            # bold replacements
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-gray-900 font-bold">\1</strong>', content)
            content = re.sub(r'`(.*?)`', r'<code class="px-1.5 py-0.5 rounded bg-gray-100 text-blue-700 font-mono text-[11px]">\1</code>', content)
            html_out.append(f'<li>{content}</li>')
        elif stripped.startswith('---'):
            html_out.append('<hr class="border-gray-200 my-6">')
        elif stripped.startswith('> '):
            html_out.append(f'<div class="bg-blue-50/70 border-l-4 border-blue-500 p-3 rounded-r-lg my-3 text-xs text-blue-950 italic">{stripped[2:]}</div>')
        # Images
        elif stripped.startswith('!['):
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
            if img_match:
                alt = img_match.group(1)
                src = img_match.group(2)
                html_out.append(f'<div class="my-4 text-center"><img src="{src}" alt="{alt}" class="rounded-xl border border-gray-200 shadow-sm max-h-[450px] mx-auto"><p class="text-xs text-gray-400 mt-1 italic">{alt}</p></div>')
        # Tables
        elif '|' in stripped:
            # Let simple table line render
            html_out.append(f'<div class="text-xs text-gray-700 font-mono py-0.5">{stripped}</div>')
        else:
            p_content = stripped
            p_content = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-gray-900 font-bold">\1</strong>', p_content)
            p_content = re.sub(r'`(.*?)`', r'<code class="px-1.5 py-0.5 rounded bg-gray-100 text-blue-700 font-mono text-[11px]">\1</code>', p_content)
            html_out.append(f'<p class="text-xs sm:text-sm text-gray-700 leading-relaxed my-2">{p_content}</p>')

    if in_list:
        html_out.append('</ul>')

    return '\n'.join(html_out)


def main():
    dirs = [d for d in BASE_DIR.iterdir() if d.is_dir()]
    dirs.sort(key=lambda x: x.name)

    for d in dirs:
        readme_path = d / "README.md"
        index_html_path = d / "index.html"

        # If index.html already exists, check if it's already there
        if index_html_path.exists():
            print(f"Skipping (already exists): {d.name}")
            continue

        if not readme_path.exists():
            print(f"No README found in {d.name}, skipping.")
            continue

        print(f"Generating index.html for: {d.name}")
        with open(readme_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        title = d.name
        # clean title
        title_clean = re.sub(r'^\d+\.\s*', '', title)

        body_html = convert_markdown_to_html(md_content)
        rendered_html = HTML_TEMPLATE.format(title=title_clean, body_html=body_html)

        with open(index_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

    print("All System Design folders now have dedicated README.md and index.html!")

if __name__ == "__main__":
    main()
