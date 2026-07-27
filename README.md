### Hi, I'm Alberto 👋

Postdoctoral Researcher in AI at **AIRLab, Politecnico di Milano**.

I work on **tabular foundation models**, **federated learning**, and **survival analysis** — building models that learn from private, distributed healthcare data.

🌐 [archettialberto.github.io](https://archettialberto.github.io) ·
🎓 [Google Scholar](https://scholar.google.com/citations?user=--kj4bcAAAAJ&hl=en) ·
💼 [LinkedIn](https://www.linkedin.com/in/albertoarchetti/) ·
📫 [alberto.archetti@polimi.it](mailto:alberto.archetti@polimi.it)

---

## Guide

This repo builds my CV (LaTeX → PDF) and website (Astro) from the YAML/BibTeX files in `data/`.

### 1. Install the environment

```bash
conda env create -f environment.yaml   # creates the 'cv' env (Python 3.12 + Poetry)
conda activate cv
poetry install                         # installs the `cv` CLI
cd website && npm install && cd ..     # website dependencies
```

For PDF output you also need **TeX Live** (with `xelatex`, `biber`, and the `svg` package).

### 2. Modify the CV

- Edit the files in `data/` (`employment.yaml`, `publications.bib`, `talks.yaml`, …).
- Validate with `cv data`.
- Optional: `cv scholar --scholar-id --kj4bcAAAAJ` pulls citation metrics and appends new publications (review them by hand).
- Optional: `cv theme list` / `cv theme use NAME` switches the visual theme.

### 3. Build

```bash
cv build-cv    # CV → cv/build/, PDF published to website/public/cv/archetti-cv.pdf
cv build-site  # exports site.json + theme.css for the website
```

Preview the website with `cd website && npm run dev` → `http://localhost:4321/`.

**Shortcut:** `./scripts/dev.sh` does all of the above (Scholar fetch, CV, site export, dev server). Use `--no-scholar` / `--no-compile` to skip steps.

### 4. Publish

```bash
git add -A
git commit -m "Update CV"
git push
```

Pushing to `main` triggers GitHub Actions, which builds the Astro site and deploys it to GitHub Pages. **CI only runs `npm run build`** — it does not regenerate data or PDFs, so always commit the generated files (`website/src/data/site.json`, `website/public/cv/archetti-cv.pdf`, theme CSS) along with your changes.
