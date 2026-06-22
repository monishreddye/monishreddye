#!/usr/bin/env python3
"""Download and restructure Hire IT People resume pages.

The target site renders resume text in HTML but often prevents easy manual
selection in a browser. This script extracts the server-rendered resume body
and converts it into structured JSON or a readable Markdown document.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_URL = (
    "https://www.hireitpeople.com/resume-database/"
    "64-java-developers-architects-resumes/"
    "63464-senior-java-developer-resume-new-york-ny"
)

BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass(frozen=True)
class TextBlock:
    """A normalized block of text from the resume body."""

    kind: str
    text: str


class TextOnlyParser(HTMLParser):
    """Convert a small HTML fragment into plain text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return clean_text(" ".join(self._parts))


class ResumeBodyParser(HTMLParser):
    """Extract paragraph/list blocks from Hire IT People's resume body."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[TextBlock] = []
        self._in_body = False
        self._body_depth = 0
        self._current_kind: str | None = None
        self._current_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        classes = attrs_dict.get("class", "").split()

        if not self._in_body and tag == "div" and "single-post-body" in classes:
            self._in_body = True
            self._body_depth = 1
            return

        if not self._in_body:
            return

        if tag not in VOID_TAGS:
            self._body_depth += 1

        if tag in BLOCK_TAGS:
            self._flush_current()
            self._current_kind = "list_item" if tag == "li" else "paragraph"
        elif tag == "br":
            self._current_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self._in_body:
            return

        if tag in BLOCK_TAGS:
            self._flush_current()

        if tag not in VOID_TAGS:
            self._body_depth -= 1
            if self._body_depth <= 0:
                self._flush_current()
                self._in_body = False

    def handle_data(self, data: str) -> None:
        if self._in_body and self._current_kind is not None:
            self._current_parts.append(data)

    def close(self) -> None:
        super().close()
        self._flush_current()

    def _flush_current(self) -> None:
        text = clean_text(" ".join(self._current_parts))
        if text:
            self.blocks.append(TextBlock(self._current_kind or "paragraph", text))
        self._current_kind = None
        self._current_parts = []


def clean_text(value: str) -> str:
    """Normalize whitespace and common HTML entities."""

    value = unescape(value).replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_tags(fragment: str) -> str:
    parser = TextOnlyParser()
    parser.feed(fragment)
    parser.close()
    return parser.get_text()


def fetch_html(url: str, timeout: int = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; resume-restructure-script/1.0; "
                "+https://www.python.org/)"
            )
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not download {url!r}: {exc}") from exc


def extract_metadata(html: str, source_url: str | None) -> dict[str, Any]:
    title = first_tag_text(html, "h3") or title_from_head(html)
    page_title = title_from_head(html)
    location = first_matching_tag_text(html, "h4", class_fragment="text-greish")

    rating_match = re.search(
        r"<span>\s*<b>\s*([0-9.]+)\s*</b>\s*<small>\s*/\s*([0-9.]+)\s*</small>",
        html,
        flags=re.IGNORECASE,
    )
    rating = None
    if rating_match:
        rating = {"score": float(rating_match.group(1)), "scale": float(rating_match.group(2))}

    return {
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "page_title": page_title,
        "location": location,
        "rating": rating,
    }


def first_tag_text(html: str, tag: str) -> str | None:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return strip_tags(match.group(1))


def first_matching_tag_text(html: str, tag: str, class_fragment: str) -> str | None:
    pattern = rf"<{tag}\b(?=[^>]*class=[\"'][^\"']*{re.escape(class_fragment)}[^\"']*[\"'])[^>]*>(.*?)</{tag}>"
    match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return strip_tags(match.group(1))


def title_from_head(html: str) -> str | None:
    raw_title = first_tag_text(html, "title")
    if not raw_title:
        return None
    return re.split(r"\s+-\s+Hire IT People\b", raw_title, maxsplit=1)[0].strip()


def extract_body_blocks(html: str) -> list[TextBlock]:
    parser = ResumeBodyParser()
    parser.feed(html)
    parser.close()
    if not parser.blocks:
        raise ValueError("Could not find a resume body. Expected a div with class 'single-post-body'.")
    return parser.blocks


def parse_resume(
    html: str,
    source_url: str | None = None,
    *,
    include_metadata: bool = False,
    include_raw: bool = False,
) -> dict[str, Any]:
    blocks = extract_body_blocks(html)
    metadata = extract_metadata(html, source_url)
    resume = {"location": metadata.get("location"), **structure_blocks(blocks)}
    if include_metadata:
        resume["metadata"] = {key: value for key, value in metadata.items() if key != "location"}
    if include_raw:
        resume["raw_text"] = blocks_to_text(blocks)
    return prune_empty(resume)


def structure_blocks(blocks: list[TextBlock]) -> dict[str, Any]:
    objective: list[str] = []
    summary: list[str] = []
    specialties: list[str] = []
    skills: dict[str, list[str]] = {}
    other_sections: dict[str, list[str]] = {}

    work_start = find_heading_index(blocks, "work experience summary")
    top_blocks = blocks[:work_start] if work_start is not None else blocks
    work_blocks = blocks[work_start + 1 :] if work_start is not None else []

    current_section: str | None = None
    for block in top_blocks:
        heading = normalized_heading(block.text)
        if heading in {"objective", "summary", "specialties", "skills"}:
            current_section = heading
            continue

        if current_section == "objective":
            objective.append(block.text)
        elif current_section == "summary":
            summary.append(block.text)
        elif current_section == "specialties":
            specialties.append(block.text)
        elif current_section == "skills":
            label, value = split_label(block.text)
            if label and value:
                skills[label] = split_values(value)
            elif block.text:
                other_sections.setdefault("skills_unparsed", []).append(block.text)
        elif block.text:
            other_sections.setdefault("unclassified", []).append(block.text)

    return {
        "objective": " ".join(objective).strip(),
        "summary": " ".join(summary).strip(),
        "specialties": specialties,
        "skills": skills,
        "work_experience": parse_work_experience(work_blocks),
        "other_sections": other_sections,
    }


def find_heading_index(blocks: list[TextBlock], heading: str) -> int | None:
    for index, block in enumerate(blocks):
        if normalized_heading(block.text) == heading:
            return index
    return None


def normalized_heading(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"\s*:+\s*$", "", text)
    return text.lower()


def split_label(text: str) -> tuple[str | None, str | None]:
    match = re.match(r"^\s*([^:]{1,80})\s*:\s*(.+?)\s*$", text)
    if not match:
        return None, None
    return clean_text(match.group(1)), clean_text(match.group(2))


def split_values(value: str) -> list[str]:
    return [part for part in (clean_text(item) for item in value.split(",")) if part]


def parse_work_experience(blocks: list[TextBlock]) -> list[dict[str, Any]]:
    experiences: list[dict[str, Any]] = []
    index = 0

    while index < len(blocks):
        while index < len(blocks) and not blocks[index].text:
            index += 1
        if index >= len(blocks):
            break

        company = blocks[index].text
        index += 1

        role = None
        if index < len(blocks) and not is_work_label(blocks[index].text):
            role = blocks[index].text
            index += 1

        experience: dict[str, Any] = {
            "company": company,
            "title": role,
            "project_description": "",
            "responsibilities": [],
            "environment": [],
            "notes": [],
        }

        collecting_responsibilities = False
        while index < len(blocks):
            block = blocks[index]
            text = block.text

            project_description = extract_prefixed_value(text, "Project Description")
            environment = extract_prefixed_value(text, "Environment")
            responsibility_heading = normalized_heading(text) in {"responsibilities", "responsibility"}

            if project_description is not None:
                experience["project_description"] = project_description
                collecting_responsibilities = False
            elif responsibility_heading:
                collecting_responsibilities = True
            elif environment is not None:
                experience["environment"] = split_values(environment)
                index += 1
                break
            elif collecting_responsibilities:
                experience["responsibilities"].append(text)
            else:
                experience["notes"].append(text)

            index += 1

        experiences.append(experience)

    return experiences


def is_work_label(text: str) -> bool:
    return (
        extract_prefixed_value(text, "Project Description") is not None
        or extract_prefixed_value(text, "Environment") is not None
        or normalized_heading(text) in {"responsibilities", "responsibility"}
    )


def extract_prefixed_value(text: str, label: str) -> str | None:
    match = re.match(rf"^\s*{re.escape(label)}\s*:\s*(.*?)\s*$", text, flags=re.IGNORECASE)
    if not match:
        return None
    return clean_text(match.group(1))


def blocks_to_text(blocks: Iterable[TextBlock]) -> str:
    lines = []
    for block in blocks:
        prefix = "- " if block.kind == "list_item" else ""
        lines.append(f"{prefix}{block.text}")
    return "\n".join(lines)


def prune_empty(value: Any) -> Any:
    if isinstance(value, dict):
        pruned = {}
        for key, nested_value in value.items():
            nested_value = prune_empty(nested_value)
            if nested_value not in (None, "", [], {}):
                pruned[key] = nested_value
        return pruned
    if isinstance(value, list):
        return [nested_value for item in value if (nested_value := prune_empty(item)) not in (None, "", [], {})]
    return value


def resume_to_markdown(resume: dict[str, Any]) -> str:
    lines: list[str] = []
    if resume.get("location"):
        lines.extend([f"**Location:** {resume['location']}", ""])

    add_text_section(lines, "Objective", resume.get("objective"))
    add_text_section(lines, "Summary", resume.get("summary"))
    add_list_section(lines, "Specialties", resume.get("specialties") or [])

    skills = resume.get("skills") or {}
    if skills:
        lines.extend(["## Skills", ""])
        for label, values in skills.items():
            lines.append(f"- **{label}:** {', '.join(values)}")
        lines.append("")

    work_experience = resume.get("work_experience") or []
    if work_experience:
        lines.extend(["## Work Experience", ""])
        for experience in work_experience:
            lines.append(f"### {experience.get('title') or 'Role'}")
            if experience.get("company"):
                lines.append(f"**Company:** {experience['company']}")
            if experience.get("project_description"):
                lines.extend(["", f"**Project Description:** {experience['project_description']}"])
            responsibilities = experience.get("responsibilities") or []
            if responsibilities:
                lines.extend(["", "**Responsibilities:**"])
                lines.extend(f"- {item}" for item in responsibilities)
            environment = experience.get("environment") or []
            if environment:
                lines.extend(["", f"**Environment:** {', '.join(environment)}"])
            notes = experience.get("notes") or []
            if notes:
                lines.extend(["", "**Notes:**"])
                lines.extend(f"- {item}" for item in notes)
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def add_text_section(lines: list[str], title: str, value: str | None) -> None:
    if value:
        lines.extend([f"## {title}", "", value, ""])


def add_list_section(lines: list[str], title: str, values: list[str]) -> None:
    if values:
        lines.extend([f"## {title}", ""])
        lines.extend(f"- {value}" for value in values)
        lines.append("")


def write_csv(resume: dict[str, Any], output_path: Path) -> None:
    """Write work experience rows to CSV for spreadsheet use."""

    fieldnames = [
        "location",
        "company",
        "job_title",
        "project_description",
        "responsibilities",
        "environment",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for experience in resume.get("work_experience", []):
            writer.writerow(
                {
                    "location": resume.get("location"),
                    "company": experience.get("company"),
                    "job_title": experience.get("title"),
                    "project_description": experience.get("project_description"),
                    "responsibilities": " | ".join(experience.get("responsibilities", [])),
                    "environment": ", ".join(experience.get("environment", [])),
                }
            )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape a Hire IT People resume page and restructure it into JSON, Markdown, or CSV."
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="Resume URL to scrape.")
    parser.add_argument(
        "-f",
        "--format",
        choices=("json", "markdown", "csv"),
        default="json",
        help="Output format. CSV contains one row per work experience item.",
    )
    parser.add_argument("-o", "--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include page/source metadata under a separate metadata key. Off by default.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include plain text extracted from the selected resume area. Off by default.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        html = fetch_html(args.url, timeout=args.timeout)
        resume = parse_resume(
            html,
            args.url,
            include_metadata=args.include_metadata,
            include_raw=args.include_raw,
        )
    except Exception as exc:  # pragma: no cover - exercised by users at runtime
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else None
    if args.format == "json":
        payload = json.dumps(resume, indent=2, ensure_ascii=False)
        write_text_or_stdout(payload + "\n", output_path)
    elif args.format == "markdown":
        write_text_or_stdout(resume_to_markdown(resume), output_path)
    else:
        if output_path is None:
            writer = csv.writer(sys.stdout)
            writer.writerow(
                [
                    "location",
                    "company",
                    "job_title",
                    "project_description",
                    "responsibilities",
                    "environment",
                ]
            )
            for experience in resume.get("work_experience", []):
                writer.writerow(
                    [
                        resume.get("location"),
                        experience.get("company"),
                        experience.get("title"),
                        experience.get("project_description"),
                        " | ".join(experience.get("responsibilities", [])),
                        ", ".join(experience.get("environment", [])),
                    ]
                )
        else:
            write_csv(resume, output_path)

    return 0


def write_text_or_stdout(payload: str, output_path: Path | None) -> None:
    if output_path is None:
        print(payload, end="")
    else:
        output_path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
