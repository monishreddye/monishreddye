# Hire IT People resume scraper

This repository contains a Python command-line program that downloads a Hire IT
People resume page and restructures the resume into machine-readable data.

The script is useful for pages where the text is visible in the browser but hard
to select or copy manually.

## Usage

Run with Python 3. No third-party packages are required.

```bash
python3 hireitpeople_resume_scraper.py \
  "https://www.hireitpeople.com/resume-database/64-java-developers-architects-resumes/63464-senior-java-developer-resume-new-york-ny"
```

By default the program prints structured JSON containing:

- title, location, rating, source URL, and scrape timestamp
- objective and summary
- specialties
- skills grouped by category
- work experience entries with company, title, project description,
  responsibilities, and environment
- raw resume text

Save JSON to a file:

```bash
python3 hireitpeople_resume_scraper.py -o resume.json
```

Create a Markdown version:

```bash
python3 hireitpeople_resume_scraper.py --format markdown -o resume.md
```

Create a CSV file with one row per work experience item:

```bash
python3 hireitpeople_resume_scraper.py --format csv -o work_experience.csv
```

The target URL from the request is built in as the default, so you can omit the
URL when scraping that resume.

## Tests

```bash
python3 -m unittest
```
