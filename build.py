"""Build the Pannoesis blog from Markdown. Run: python3 build.py"""

from html import escape
from pathlib import Path
import re

from markdown_it import MarkdownIt


ROOT = Path(__file__).parent
SLUG = "neuro-symbolic-agents"
TITLE = "Neuro-Symbolic Agents: From Plausible Answers to Supported Claims"
SUMMARY = "How neural interpretation, ontologies, and evidence-backed inference turn plausible answers into supported claims."
DATE = "25 September 2026"
URL = f"https://pannoesis.github.io/posts/{SLUG}.html"


def page(title: str, description: str, content: str, *, article: bool = False) -> str:
    script = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>' if article else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta property="og:type" content="{'article' if article else 'website'}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{URL if article else 'https://pannoesis.github.io/'}">
  <title>{escape(title)} · Pannoesis</title>
  <link rel="canonical" href="{URL if article else 'https://pannoesis.github.io/'}">
  <link rel="stylesheet" href="{'../' if article else ''}assets/style.css">
  <link rel="icon" type="image/png" href="{'../' if article else ''}assets/pannoesis-logo.png">
  {script}
</head>
<body>
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="{'../index.html' if article else 'index.html'}" aria-label="Pannoesis home"><span class="brand-mark"><img src="{'../' if article else ''}assets/pannoesis-logo.png" alt=""></span><span>Pannoesis<span class="brand-dot">.</span></span></a>
      <span class="header-label">Ideas &amp; engineering</span>
    </header>
    {content}
    <footer class="site-footer"><span>© 2026 Pannoesis</span><span>Thoughts on building systems that can show their work.</span></footer>
  </div>
</body>
</html>
"""


def render_markdown(source: str) -> str:
    """Keep TeX intact while Markdown handles prose, links, and tables."""
    maths: list[str] = []

    def protect(match: re.Match[str]) -> str:
        index = len(maths)
        block = match.group().startswith("$$")
        formula = match.group()[2:-2] if block else match.group()[1:-1]
        maths.append(
            f'<div class="equation">\\[{escape(formula)}\\]</div>'
            if block else f'<span class="inline-equation">\\({escape(formula)}\\)</span>'
        )
        return f"MATHPLACEHOLDER{index}END"

    protected = re.sub(r"\$\$[\s\S]*?\$\$|(?<!\$)\$(?!\$)[^\n$]+\$(?!\$)", protect, source)
    html = MarkdownIt("commonmark").enable("table").render(protected)
    for index, formula in enumerate(maths):
        marker = f"MATHPLACEHOLDER{index}END"
        html = html.replace(f"<p>{marker}</p>", formula) if formula.startswith("<div") else html
        html = html.replace(marker, formula)
    return html


def main() -> None:
    source = (ROOT / "posts" / f"{SLUG}.md").read_text()
    body = render_markdown(source)
    body = re.sub(r"<h1>.*?</h1>\n", "", body, count=1)
    article = f"""<main class="article-layout" id="main">
      <a class="back-link" href="../index.html">← All writing</a>
      <div class="article-kicker">Essay <span aria-hidden="true">/</span> AI systems</div>
      <h1>{escape(TITLE)}</h1>
      <p class="article-deck">{escape(SUMMARY)}</p>
      <div class="article-meta"><span>By Pannoesis</span><span aria-hidden="true">·</span><time datetime="2026-09-25">{DATE}</time></div>
      <div class="article-rule"></div>
      <article class="prose">{body}</article>
      <div class="article-end"><a href="../index.html">← Back to all writing</a></div>
    </main>"""
    (ROOT / "posts" / f"{SLUG}.html").write_text(page(TITLE, SUMMARY, article, article=True))

    home = f"""<main id="main">
      <section class="hero" aria-labelledby="hero-title">
        <div class="eyebrow"><span class="eyebrow-line"></span> THE PANNOESIS JOURNAL</div>
        <h1 id="hero-title">Ideas with<br><em>evidence behind them.</em></h1>
        <p>Notes on intelligence, knowledge, and the systems we build to connect them.</p>
      </section>
      <section class="latest" aria-labelledby="latest-title">
        <div class="section-heading"><h2 id="latest-title">Latest writing</h2><span>01 / 01</span></div>
        <a class="post-card" href="posts/{SLUG}.html">
          <div class="post-info"><span>AI systems</span><span>{DATE}</span></div>
          <h3>{escape(TITLE)}</h3>
          <p>{escape(SUMMARY)}</p>
          <span class="read-link">Read article <span aria-hidden="true">↗</span></span>
        </a>
      </section>
    </main>"""
    (ROOT / "index.html").write_text(page("Ideas & engineering", "The Pannoesis journal on intelligence, knowledge, and evidence.", home))


if __name__ == "__main__":
    main()
