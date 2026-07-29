# Matteo Matteucci

Full Professor of Computer Engineering at the **Department of Electronics,
Information and Bioengineering, Politecnico di Milano**.

My research spans **robotics**, **machine learning**, **computer vision**, and
**pattern recognition**, with applications in autonomous systems, intelligent
vehicles, agriculture, and assistive technologies.

[Website](https://matteucci.github.io) ·
[Google Scholar](https://scholar.google.com/citations?user=PdbEg5YAAAAJ&hl=en) ·
[LinkedIn](https://www.linkedin.com/in/matteo-matteucci-a5b59717/) ·
[Email](mailto:matteo.matteucci@polimi.it)

## Repository guide

This repository builds the website and academic CV from the YAML and BibTeX
files in `data/`.

### Install

```bash
conda env create -f environment.yaml
conda activate cv
poetry install
cd website && npm install && cd ..
```

PDF generation additionally requires TeX Live with `xelatex`, `biber`, and the
`svg` package.

### Update content

- Edit the structured files in `data/`.
- Validate with `cv data`.
- Optionally refresh Scholar data with
  `cv scholar --scholar-id PdbEg5YAAAAJ`; review imported publications before
  committing them.
- Use `cv theme list` and `cv theme use NAME` to inspect or switch themes.

### Build

```bash
cv build-cv
cv build-site
cd website && npm run build
```

The generated PDF is published at `website/public/cv/matteucci-cv.pdf`.
`./scripts/dev.sh` provides the complete local workflow; pass `--no-scholar`
or `--no-compile` when appropriate.

Pushing to `main` triggers the GitHub Pages workflow. Commit generated
`website/src/data/site.json`, the published PDF, and generated theme assets
together with the source changes.
