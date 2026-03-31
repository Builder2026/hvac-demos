# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A GitHub Pages site (`demos.kinesiscreatives.com`) that hosts personalized HVAC demo websites for cold outreach. Each HTML file is a standalone demo site for one HVAC business, generated from a single template and a leads spreadsheet.

## How to generate demo sites

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 generate.py           # full run
python3 generate.py --test 3  # test on 3 businesses
```

Reads `leads_enriched.csv` (must exist — produced by `scrape.py`), filters rows with a valid email, deduplicates by name+city, calls Claude API (claude-haiku) to generate a unique tagline and personalized email line per business, injects a unique font pairing + color palette per site, and writes HTML files to the **repo root**. Also writes `leads_with_personalization.csv` with tagline and email_line columns.

Dependencies (`pandas`, `anthropic`) are auto-installed on first run. Requires `ANTHROPIC_API_KEY` env var.

## Design system (per-site theming)

`generate.py` deterministically picks a unique palette and font pairing per business based on `md5(name|city)`. 8 palettes and 10 Google Font pairings are defined in `generate.py`. The overrides are injected as a `:root {}` block at the top of the template's `<style>` tag and the font `<link>` is swapped.

## Template and placeholders

`template.html` is the single source of truth for all demo sites. It uses these placeholders:

| Placeholder | Source |
|---|---|
| `{{BUSINESS_NAME}}` | `name` column |
| `{{BUSINESS_NAME_SHORT}}` | First word of name |
| `{{CITY}}` | `city` column |
| `{{PHONE}}` | `phone` column |
| `{{PHONE_RAW}}` | Digits and `+` only |
| `{{RATING}}` | `rating` column |
| `{{REVIEW_COUNT}}` | `reviews` column (integer) |
| `{{STARS_HTML}}` | `★` repeated by rounded rating |
| `{{EMAIL}}` | `email` column |
| `{{ADDRESS}}` | `address` column |
| `{{TAGLINE}}` | Claude-generated 1-sentence hero tagline |
| `{{REVIEW_1_TEXT}}` … `{{REVIEW_3_DATE}}` | Removed — no fake reviews in current version |

## File naming convention

HTML files are named `[city-slug]-[business-name-slug].html` using this slugify logic:
- Lowercase, strip leading/trailing whitespace
- Remove characters not in `[a-z0-9_\s-]`
- Collapse whitespace/underscores to `-`
- Collapse multiple `-` to one

Files live at the **repo root** (not in a subfolder) so URLs are `demos.kinesiscreatives.com/filename.html`.

## Lead data files

- `leads.xlsx` — merged master spreadsheet (from multiple Outscraper exports, deduped by phone)
- `leads_enriched.csv` — full Outscraper data + `confirmed_phone`, `confirmed_website`, `scraped_rating`, `scraped_address` from Google Maps scraper (`scrape.py`)
- `leads_with_personalization.csv` — one row per unique business with `tagline` and `email_line` from Claude
- `all_leads_with_email.csv` — 441 leads with valid emails, includes `demo_url` column
- `hvac_upload.csv` — 751 unique emails, HVAC-category filtered, deduped by email, includes `demo_url`
- `leads_upload.csv` — trimmed upload-ready file: `email, name, city, phone, rating, reviews, demo_url`

These data files are gitignored and not in the repo.

## Conventions and past mistakes to avoid

- Always use `python3`, not `python` — `python` is not on PATH on this machine
- The template file is `template.html` (not `hvac-demo-template.html` — it was renamed)
- HTML files go to the **repo root**, not `output/` — the `output/` folder exists but is gitignored
- When filtering emails, treat `"nan"` strings as empty (pandas reads missing values as the string `"nan"` after CSV round-trips)
- Full Outscraper data (with `subtypes`, `category`, etc.) lives in `leads_with_urls.csv` — the trimmed CSVs (`hvac_upload.csv`, `leads_upload.csv`) have only 7 columns and lack those fields

## Deploying

```bash
git add *.html
git commit -m "..."
git push
```

GitHub Pages serves the repo root at `demos.kinesiscreatives.com` (configured via `CNAME` file).
