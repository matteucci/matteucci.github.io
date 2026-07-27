"""Command-line entry point.

    cv data           validate + summarise the data layer
    cv build-cv       render LaTeX (and compile if xelatex is present)
    cv build-site     export data/site.json for the Astro website
    cv scholar        (opt-in) fetch citation metrics from Google Scholar
    cv theme list     list available themes
    cv theme use NAME switch the active theme
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import typer

from .loader import ROOT, load
from .render_cv import BUILD_DIR, render

app = typer.Typer(add_completion=False, help="Build Alberto Archetti's CVs and website from data/.")

theme_app = typer.Typer(add_completion=False, help="Inspect and switch the active visual theme.")
app.add_typer(theme_app, name="theme")


@theme_app.command("list")
def theme_list() -> None:
    """List available themes (theme/themes/*.yaml), marking the active one."""
    from .theme import active_theme_name, list_themes

    active = active_theme_name()
    for name in list_themes():
        marker = typer.style("● active", fg=typer.colors.GREEN) if name == active else ""
        typer.echo(f"  {name:14} {marker}")


@theme_app.command("show")
def theme_show() -> None:
    """Print the active theme's palette and fonts."""
    from .theme import active_theme_name, load_theme

    t = load_theme()
    typer.secho(f"Active theme: {active_theme_name()}", fg=typer.colors.CYAN)
    typer.echo("Colors:")
    for name, hexval in t["colors"].items():
        typer.echo(f"  {name:12} #{hexval}")
    typer.echo("Fonts:")
    for role, spec in t["fonts"].items():
        typer.echo(f"  {role:8} {spec.get('web_family', spec['family'])}")


@theme_app.command("use")
def theme_use(name: str = typer.Argument(..., help="Theme name (see `cv theme list`).")) -> None:
    """Switch the active theme. Re-run build-cv / build-site to apply it."""
    from .theme import list_themes, set_active_theme

    try:
        set_active_theme(name)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Active theme set to '{name}'.", fg=typer.colors.GREEN)
    # Recolor the logo to match the new theme's accent.
    import sys

    sys.path.insert(0, str(ROOT))
    from logo.compose import generate_for_theme

    generate_for_theme()
    typer.echo("Logo recolored for the new theme.")
    typer.echo(f"Available: {', '.join(list_themes())}")
    typer.echo("Now run: python -m src.cli build-cv  &&  python -m src.cli build-site")


@app.command()
def data() -> None:
    """Validate the data layer and print a summary."""
    d = load()
    typer.echo(f"Profile     : {d.profile.full_name} — {d.profile.title}")
    typer.echo(f"Employment  : {len(d.employment)}")
    typer.echo(f"Education   : {len(d.education)}")
    typer.echo(f"Teaching    : {len(d.teaching)}")
    typer.echo(f"Awards      : {len(d.awards)}")
    typer.echo(f"Projects    : {len(d.projects)}")
    typer.echo(f"Publications: {len(d.publications)}")
    if d.metrics:
        typer.echo(f"Metrics     : h-index {d.metrics.h_index}, citations {d.metrics.total_citations}")
    typer.secho("OK — data validates.", fg=typer.colors.GREEN)


@app.command("build-cv")
def build_cv(
    compile_pdf: bool = typer.Option(True, "--compile/--no-compile", help="Run xelatex if available."),
) -> None:
    """Render the CV to LaTeX, and compile to PDF if xelatex is installed."""
    d = load()
    tex = render(d)
    typer.secho(f"Wrote {tex.relative_to(ROOT)}", fg=typer.colors.GREEN)

    xelatex = shutil.which("xelatex")
    if not compile_pdf or not xelatex:
        if compile_pdf and not xelatex:
            typer.secho(
                "xelatex not found — emitted .tex only. Install TeX Live "
                "(needs xelatex + biber + the 'svg' package), then re-run.",
                fg=typer.colors.YELLOW,
            )
        return
    _compile(tex, surname=d.profile.name.split()[-1].lower())


@app.command("build-theme")
def build_theme() -> None:
    """Generate website/src/styles/theme.css from theme/theme.yaml."""
    from .theme import write_web_css

    out = write_web_css()
    typer.secho(f"Wrote {out.relative_to(ROOT)}", fg=typer.colors.GREEN)


@app.command("build-logo")
def build_logo(variant: str = typer.Option("two-tone", help="two-tone | outline-back | ghost-back")) -> None:
    """Regenerate the double-A logo in the active theme's accent color."""
    import sys

    sys.path.insert(0, str(ROOT))
    from logo.compose import generate_for_theme

    written = generate_for_theme(variant)
    for name, path in written.items():
        typer.secho(f"Wrote {path.relative_to(ROOT)}", fg=typer.colors.GREEN)


@app.command("build-site")
def build_site() -> None:
    """Export data + theme for the Astro website (site.json + theme.css)."""
    from .theme import write_web_css

    d = load()
    out = ROOT / "website" / "src" / "data" / "site.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(d.model_dump_json(indent=2), encoding="utf-8")
    typer.secho(f"Wrote {out.relative_to(ROOT)}", fg=typer.colors.GREEN)

    css = write_web_css()
    typer.secho(f"Wrote {css.relative_to(ROOT)}", fg=typer.colors.GREEN)


@app.command()
def scholar(
    scholar_id: str = typer.Option(..., help="Google Scholar user ID (the ?user= value)."),
) -> None:
    """Sync from Google Scholar: write metrics to scholar_cache.json and append
    any new publications to publications.bib (existing entries are never changed).

    Opt-in and best-effort: Scholar may rate-limit or block.
    """
    from .scholar import append_new_publications, fetch_scholar

    data = fetch_scholar(scholar_id)
    out = ROOT / "data" / "scholar_cache.json"
    # Don't store the candidate pub list in the cache; it's only for appending.
    pubs = data.pop("publications", [])
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    typer.secho(f"Wrote {out.relative_to(ROOT)}", fg=typer.colors.GREEN)

    bib = ROOT / "data" / "publications.bib"
    added = append_new_publications(pubs, bib)
    if added:
        typer.secho(f"Added {len(added)} new publication(s) to {bib.relative_to(ROOT)}:",
                    fg=typer.colors.GREEN)
        for k in added:
            typer.echo(f"  + {k}")
        typer.secho("Review/tidy the new entries (author order, venue, keywords) by hand.",
                    fg=typer.colors.YELLOW)
    else:
        typer.echo("No new publications — publications.bib already covers Scholar.")


def _compile(tex: Path, surname: str) -> None:
    # Run twice so page-number outlines / refs settle in multi-page CVs.
    cmd = ["xelatex", "-interaction=nonstopmode", "-shell-escape", tex.name]
    typer.echo(f"Compiling: {' '.join(cmd)}  (cwd={BUILD_DIR})")
    res = None
    for _ in range(2):
        res = subprocess.run(cmd, cwd=BUILD_DIR, capture_output=True, text=True, check=False)

    pdf = (BUILD_DIR / tex.stem).with_suffix(".pdf")
    # xelatex returns nonzero on harmless overfull-hbox warnings, so trust the
    # presence of the PDF rather than the exit code.
    if not pdf.exists():
        typer.secho("xelatex failed; tail of log:", fg=typer.colors.RED)
        typer.echo("\n".join((res.stdout if res else "").splitlines()[-25:]))
        raise typer.Exit(1)
    typer.secho(f"PDF: {pdf.relative_to(ROOT)}", fg=typer.colors.GREEN)

    # Publish the CV to the website's public/ so the same PDF is downloadable
    # and tracked, named after the profile surname (e.g. archetti-cv.pdf).
    published = ROOT / "website" / "public" / "cv" / f"{surname}-cv.pdf"
    published.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, published)
    typer.secho(f"Published: {published.relative_to(ROOT)}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
