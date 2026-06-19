# Paper 53 VLA Highlight Hardening Plan

Date: 2026-06-20

## Objective

Harden the visual highlight/link-box styling in Paper 53 so it matches the VLA-v4 role-model PDF's professional red and green boxed callouts while preserving the final full-scale micro-slip manuscript, results, page count, and scientific claims.

## Current Evidence

- Canonical PDF: `C:/Users/wangz/Downloads/53.pdf`.
- Current page count: 25.
- Current affected link pages: 3, 4, and 10.
- Current link annotations: 9 red internal-reference links.
- Current border state: all 9 link annotations use border `(0, 0, 0)`, so the boxes are invisible.
- Current LaTeX source uses `\hypersetup{hidelinks}` in `paper/main.tex`.
- Current final result remains the full-scale excitation-aware micro-slip benchmark: 518,400 compact condition rows, 171,694,080,000 represented evaluations, and 13,735,526,400,000 represented frame decisions.

## Role-Model Style Target

Match the VLA-v4 role model's link annotation style:

```tex
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

Expected Paper 53 result after rebuild:

- Page count remains 25.
- All 9 internal-reference link annotations remain red.
- All 9 link annotations use border `(0, 0, 1)`.
- No scientific content, benchmark data, or claim is changed.

## Execution Plan

1. Render the affected pre-change pages to `C:/Users/wangz/highlight_box_hardening/tmp/pdfs/paper53_before` for baseline visual comparison.
2. Replace `\hypersetup{hidelinks}` in `paper/main.tex` with the VLA-v4 hyperref settings above.
3. Rebuild using `scripts/build_pdf.ps1`, which exports only the canonical PDF to Downloads, records build metadata, and removes `paper/main.pdf`.
4. Verify with `pypdf` that the rebuilt PDF has 25 pages, 9 red link annotations, and 9 `(0, 0, 1)` borders.
5. Render the affected post-change pages to `C:/Users/wangz/highlight_box_hardening/tmp/pdfs/paper53_after` and visually inspect the highlight pages for professional box weight, alignment, spacing, and legibility.
6. Update README, child status, and tracked audit metadata if needed so the canonical PDF hash and visual hardening evidence match the actual output.
7. Remove Paper 53 temporary render folders after QA.
8. Commit and push the clean repo before moving to the next paper.

## Non-Goals

- Do not rerun the benchmark.
- Do not pad content or alter the 25-page manuscript to chase page count.
- Do not revise claims, tables, captions, or results unless a visual/layout defect requires a tiny local wording adjustment.
