# Meta — Technical Solutions Consultant (New York, NY) — Application Package

Tailored application materials for the Meta Technical Solutions Consultant role ($98K–$153K/yr, NYC).

## Files

| File | Description |
|---|---|
| `MonishReddyEdulakanti_Meta_TSC_Resume.pdf` | One-page tailored resume (compiled from `resume.tex`) |
| `MonishReddyEdulakanti_Meta_TSC_CoverLetter.pdf` | One-page cover letter (compiled from `cover-letter.tex`) |
| `resume.tex` / `cover-letter.tex` | LaTeX sources — compile with `tectonic <file>.tex` |

## How the resume maps to the job requirements

| Meta requirement | Where it shows up |
|---|---|
| Primary technical point of contact for partners/clients | HCLTech bullet 1 (primary contact for FedEx); ISU bullet 1 |
| 4+ yrs technical consulting / solutions engineering | HCLTech Sep 2019–Dec 2023 + ISU Mar 2024–Dec 2025 (6 yrs combined) |
| 4+ yrs web/mobile APIs, diagnosing integrations, API docs | HCLTech bullet 2 (API documentation, requests/responses, root cause, guided fixes) |
| Root-cause analysis of architectures and data flows | Summary + HCLTech bullet 2 (root causes across data flows and architectures) |
| Cross-functional collaboration for launches and support | HCLTech bullet 3 (releases, production launches, 99.9% availability) |
| Patterns → scalable fixes, tooling, automation | HCLTech bullet 4 (70% less manual effort, 15+ hrs/week saved, "support funnel" language) |
| Technical documentation and self-serve troubleshooting guides | HCLTech bullet 5 (playbooks, KB, 40% faster resolution) + ISU bullet 2 |
| Data/metrics to evaluate effectiveness and communicate outcomes | HCLTech bullet 6 |
| Guidance to peers on complex troubleshooting | HCLTech bullet 5 (mentoring peers) |
| AI-integrated workflows (preferred quals: prompt/context engineering, agent orchestration, ethical AI reviews) | Skills "AI & Automation" line, ISU bullet 2 (quality/accuracy reviews), Monish Labs bullet 2 |
| Clear recommendations for technical and non-technical audiences | Summary + HCLTech bullets 1 and 6 |

## Honest gaps (be ready to address in interviews)

- No direct Meta ads-platform experience (Conversions API, Meta Pixel, signals/measurement, attribution). The cover letter frames this as an area of eager growth; consider completing Meta Blueprint courses or a small Conversions API/Pixel demo integration before interviews to close this gap credibly.
- Client-facing experience is via HCLTech serving FedEx/USAA rather than a titled "consultant" role — lead with the "primary technical contact" framing.

## Rebuilding the PDFs

```bash
tectonic resume.tex && tectonic cover-letter.tex
```
