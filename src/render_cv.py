"""Render CV LaTeX from :class:`CVData` using Jinja2.

Jinja's default ``{{ }}`` / ``{% %}`` clash with LaTeX, so we use:
    \\VAR{ }   expressions
    \\BLOCK{ } statements
    #= =#      comments
A ``tex`` filter escapes LaTeX specials in data values.

The build dir is made self-contained — preamble, fonts, and logo assets are
copied in — so the emitted ``.tex`` compiles with a plain ``xelatex cv``.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import jinja2

from .loader import ROOT
from .models import CVData
from .theme import font_families, latex_color_defs, load_theme

CV_DIR = ROOT / "cv"
TEMPLATE_DIR = CV_DIR / "templates"
FONTS_DIR = CV_DIR / "fonts"
ASSETS_DIR = CV_DIR / "assets"
BUILD_DIR = CV_DIR / "build"

# LaTeX special characters -> escaped forms.
_TEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex_escape(value: object) -> str:
    s = str(value)
    out = []
    for ch in s:
        out.append(_TEX_REPLACEMENTS.get(ch, ch))
    result = "".join(out)
    # Prevent -- and --- from being rendered as en/em dashes by XeLaTeX ligatures.
    result = result.replace("---", "{-}{-}{-}").replace("--", "{-}{-}")
    return result


_STRONG_RE = re.compile(r"<strong>(.*?)</strong>", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def html_to_tex(value: object) -> str:
    """Convert HTML-annotated bio text to LaTeX.

    Converts <strong>…</strong> to \\textbf{…}, strips other tags,
    and escapes LaTeX specials in plain-text runs.
    """
    s = str(value).strip()
    parts = _STRONG_RE.split(s)
    # split() with a capturing group gives [plain, strong, plain, strong, …]
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out.append(tex_escape(_TAG_RE.sub("", part)))
        else:
            out.append(r"\textbf{" + tex_escape(part) + "}")
    return "".join(out)


def _env() -> jinja2.Environment:
    env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string="#=",
        comment_end_string="=#",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    )
    env.filters["tex"] = tex_escape
    env.filters["htmltex"] = html_to_tex
    return env


def render(data: CVData, template: str = "cv") -> Path:
    """Render ``<template>.tex.j2`` to ``cv/build/<template>.tex``.

    Returns the path to the written ``.tex`` file.
    """
    payload = data

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    # Make the build dir self-contained for xelatex.
    _sync_dir(FONTS_DIR, BUILD_DIR / "fonts")
    # Logos are vector PDFs (converted from SVG) so we avoid the svg/Inkscape
    # LaTeX dependency. Regenerate the PDF if the SVG is newer.
    _ensure_logo_pdfs()
    for asset in ASSETS_DIR.glob("*.pdf"):
        shutil.copy2(asset, BUILD_DIR / asset.name)

    # Theme drives colors + fonts (single source: the active theme/themes/*.yaml).
    theme = load_theme()
    fams = font_families(theme)
    disp = theme["fonts"]["display"].get("latex", {})
    txt = theme["fonts"]["text"].get("latex", {})
    theme_ctx = {
        "color_defs": latex_color_defs(theme),
        "font_display": fams["display"],
        "font_text": fams["text"],
        # Per-theme LaTeX face suffixes (fall back to old-money's defaults).
        "face_display_upright": disp.get("upright", "Regular"),
        "face_display_bold": disp.get("bold", "SemiBold"),
        "face_display_title": disp.get("title", "SemiBold"),
        "face_display_title_bold": disp.get("title_bold", "Bold"),
        "face_text_upright": txt.get("upright", "Light"),
        "face_text_bold": txt.get("bold", "Regular"),
        "face_text_italic": txt.get("italic", "Light"),
        "face_text_medium": txt.get("medium", "Medium"),
        "face_text_medium_bold": txt.get("medium_bold", "SemiBold"),
        # Letterspacing the display font (Cormorant looks good spaced; Manrope not).
        "display_letterspace": theme["fonts"]["display"].get("letterspace", "0.0"),
        "fonts_path": "fonts",
    }

    # Render the shared preamble too (it is a template: needs theme context).
    _render_to(_env(), "_preamble.tex.j2", BUILD_DIR / "_preamble.tex", **theme_ctx)

    logo = "logo-gold"
    out = BUILD_DIR / f"{template}.tex"
    _render_to(
        _env(),
        f"{template}.tex.j2",
        out,
        profile=payload.profile,
        research_interests=payload.research_interests,
        skills=payload.skills,
        employment=payload.employment,
        education=payload.education,
        teaching=payload.teaching,
        talks=payload.talks,
        supervision=payload.supervision,
        awards=payload.awards,
        projects=payload.projects,
        publications=payload.publications,
        metrics=payload.metrics,
        logo=logo,
        **theme_ctx,
    )
    return out


def _render_to(env: jinja2.Environment, template_name: str, dest: Path, **ctx: object) -> None:
    text = env.get_template(template_name).render(**ctx)
    dest.write_text(text, encoding="utf-8")


def _ensure_logo_pdfs() -> None:
    """Convert any logo SVG to PDF when the PDF is missing or stale."""
    for svg in ASSETS_DIR.glob("*.svg"):
        pdf = svg.with_suffix(".pdf")
        if pdf.exists() and pdf.stat().st_mtime >= svg.stat().st_mtime:
            continue
        try:
            import cairosvg

            cairosvg.svg2pdf(url=str(svg), write_to=str(pdf))
        except Exception:
            # No working converter (missing cairosvg or a broken native cairo):
            # rely on a pre-existing PDF if present, else skip.
            continue


def _sync_dir(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.ttf"):
        target = dst / f.name
        if not target.exists() or target.stat().st_mtime < f.stat().st_mtime:
            shutil.copy2(f, target)
