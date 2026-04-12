#!/usr/bin/env python3
"""
Deterministic citation validation + repair pipeline for Claude-generated HTML articles.

What it does
------------
1. Reads an article HTML file and an approved reference pack JSON file.
2. Validates that only approved PMIDs are cited inline.
3. Normalizes inline citation tokens to a human-readable format.
4. Rebuilds the entire References section deterministically from the approved pack.
5. Flags or removes unknown references.
6. Writes:
   - repaired HTML
   - validation report JSON

Recommended model workflow
--------------------------
- Ask Claude to write the article body and cite only with tokens like:
    [PMID:12345678]
- Do NOT ask Claude to write the final bibliography HTML.
- Run this script after generation to produce the final inline citations and references.

Reference pack JSON format
--------------------------
[
  {
    "pmid": "12345678",
    "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
    "citation_text": "Smith J, Jones P. Example paper title. Br J Sports Med. 2024.",
    "short_cite": "Smith et al., 2024"
  }
]

Usage
-----
python validate_repair_citations.py \
  --input article.html \
  --refs approved_references.json \
  --output article.repaired.html \
  --report article.validation.json

Optional flags
--------------
--strict-inline-order
    Enforces bibliography order based on first inline appearance.
--remove-unknown-inline
    Removes unknown [PMID:xxxxx] tokens from the body instead of leaving them in place.
--fail-on-unknown
    Exit non-zero if unknown inline PMIDs are found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, asdict
from html import escape
from pathlib import Path
from typing import Dict, List, Optional, Tuple


INLINE_TOKEN_RE = re.compile(r"\[PMID:(\d{4,10})\]")
REF_SECTION_RE = re.compile(
    r"(?is)<h2[^>]*>\s*References\s*</h2>\s*(<ol[^>]*>.*?</ol>|<ul[^>]*>.*?</ul>)"
)
TITLE_RE = re.compile(r"(?is)<title>(.*?)</title>")


@dataclass
class Reference:
    pmid: str
    pubmed_url: str
    citation_text: str
    short_cite: str


@dataclass
class ValidationReport:
    article_title: Optional[str]
    input_file: str
    output_file: str
    total_inline_tokens_found: int
    unique_inline_pmids_found: List[str]
    unknown_inline_pmids: List[str]
    approved_pmids_available: List[str]
    references_written: List[str]
    bibliography_order_strategy: str
    had_existing_reference_section: bool
    removed_unknown_inline_tokens: bool
    pass_status: bool
    warnings: List[str]
    errors: List[str]


def load_reference_pack(path: Path) -> Dict[str, Reference]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Reference pack must be a JSON list.")
    refs: Dict[str, Reference] = {}
    for idx, item in enumerate(raw, start=1):
        required = {"pmid", "pubmed_url", "citation_text", "short_cite"}
        missing = required - set(item.keys())
        if missing:
            raise ValueError(f"Reference #{idx} missing fields: {sorted(missing)}")
        pmid = str(item["pmid"]).strip()
        pubmed_url = str(item["pubmed_url"]).strip()
        citation_text = str(item["citation_text"]).strip()
        short_cite = str(item["short_cite"]).strip()

        if not pmid.isdigit():
            raise ValueError(f"Reference #{idx} has invalid PMID: {pmid}")
        expected_prefix = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        if pubmed_url != expected_prefix:
            raise ValueError(
                f"Reference #{idx} pubmed_url mismatch for PMID {pmid}. "
                f"Expected exactly: {expected_prefix}"
            )
        if pmid in refs:
            raise ValueError(f"Duplicate PMID in reference pack: {pmid}")

        refs[pmid] = Reference(
            pmid=pmid,
            pubmed_url=pubmed_url,
            citation_text=citation_text,
            short_cite=short_cite,
        )
    return refs


def extract_title(html: str) -> Optional[str]:
    match = TITLE_RE.search(html)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip() or None


def extract_inline_pmids(html: str) -> List[str]:
    return INLINE_TOKEN_RE.findall(html)


def ordered_unique(items: List[str]) -> List[str]:
    return list(OrderedDict.fromkeys(items).keys())


def replace_inline_tokens(
    html: str,
    ref_map: Dict[str, Reference],
    remove_unknown_inline: bool,
    warnings: List[str],
    errors: List[str],
) -> Tuple[str, List[str], List[str]]:
    """
    Replace [PMID:12345678] with clickable inline citations.

    Output format:
      (<a href="https://pubmed.ncbi.nlm.nih.gov/12345678/" ...>Smith et al., 2024</a>)
    """
    found_pmids: List[str] = []
    unknown_pmids: List[str] = []

    def repl(match: re.Match[str]) -> str:
        pmid = match.group(1)
        found_pmids.append(pmid)
        ref = ref_map.get(pmid)
        if ref is None:
            unknown_pmids.append(pmid)
            msg = f"Unknown inline PMID found: {pmid}"
            warnings.append(msg)
            if remove_unknown_inline:
                return ""
            return match.group(0)

        return (
            f'(<a href="{escape(ref.pubmed_url)}" '
            f'target="_blank" rel="noopener noreferrer">{escape(ref.short_cite)}</a>)'
        )

    replaced = INLINE_TOKEN_RE.sub(repl, html)
    if unknown_pmids and not remove_unknown_inline:
        errors.append(
            "Unknown inline PMIDs remain in the article because "
            "--remove-unknown-inline was not enabled."
        )
    return replaced, ordered_unique(found_pmids), ordered_unique(unknown_pmids)


def build_references_html(pmids_in_order: List[str], ref_map: Dict[str, Reference]) -> str:
    lines = ['<h2>References</h2>', '<ol class="references">']
    for pmid in pmids_in_order:
        ref = ref_map[pmid]
        lines.append(
            "  <li>"
            f'{escape(ref.citation_text)} '
            f'<a href="{escape(ref.pubmed_url)}" target="_blank" rel="noopener noreferrer">'
            "PubMed</a>"
            "</li>"
        )
    lines.append("</ol>")
    return "\n".join(lines)


def replace_or_append_reference_section(html: str, references_html: str) -> Tuple[str, bool]:
    if REF_SECTION_RE.search(html):
        return REF_SECTION_RE.sub(references_html, html, count=1), True

    # Append at end of body if possible, else end of doc.
    body_close = re.search(r"(?is)</body>", html)
    if body_close:
        start = body_close.start()
        return html[:start] + "\n\n" + references_html + "\n" + html[start:], False
    return html + "\n\n" + references_html + "\n", False


def run_pipeline(
    input_path: Path,
    refs_path: Path,
    output_path: Path,
    report_path: Path,
    strict_inline_order: bool,
    remove_unknown_inline: bool,
    fail_on_unknown: bool,
) -> int:
    html = input_path.read_text(encoding="utf-8")
    ref_map = load_reference_pack(refs_path)

    warnings: List[str] = []
    errors: List[str] = []

    article_title = extract_title(html)

    replaced_html, all_found_ordered, unknown_inline_pmids = replace_inline_tokens(
        html=html,
        ref_map=ref_map,
        remove_unknown_inline=remove_unknown_inline,
        warnings=warnings,
        errors=errors,
    )

    approved_used_pmids = [pmid for pmid in all_found_ordered if pmid in ref_map]

    # Bibliography order strategy.
    if strict_inline_order:
        bibliography_pmids = approved_used_pmids
        order_strategy = "first_inline_appearance"
    else:
        # stable fallback: keep first appearance anyway, but documented separately
        bibliography_pmids = approved_used_pmids
        order_strategy = "first_inline_appearance"

    references_html = build_references_html(bibliography_pmids, ref_map)
    repaired_html, had_existing_ref_section = replace_or_append_reference_section(
        replaced_html, references_html
    )

    output_path.write_text(repaired_html, encoding="utf-8")
    pass_status = True

    if not approved_used_pmids:
        warnings.append("No approved inline PMIDs found in article body.")
    if fail_on_unknown and unknown_inline_pmids:
        errors.append("Unknown inline PMIDs were found and fail-on-unknown is enabled.")
    if errors:
        pass_status = False

    report = ValidationReport(
        article_title=article_title,
        input_file=str(input_path),
        output_file=str(output_path),
        total_inline_tokens_found=len(extract_inline_pmids(html)),
        unique_inline_pmids_found=all_found_ordered,
        unknown_inline_pmids=unknown_inline_pmids,
        approved_pmids_available=sorted(ref_map.keys(), key=int),
        references_written=bibliography_pmids,
        bibliography_order_strategy=order_strategy,
        had_existing_reference_section=had_existing_ref_section,
        removed_unknown_inline_tokens=remove_unknown_inline,
        pass_status=pass_status,
        warnings=warnings,
        errors=errors,
    )
    report_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    return 0 if pass_status else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and repair citation structure in Claude-generated HTML articles."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input HTML file")
    parser.add_argument("--refs", required=True, type=Path, help="Approved references JSON")
    parser.add_argument("--output", required=True, type=Path, help="Repaired HTML output")
    parser.add_argument("--report", required=True, type=Path, help="Validation report JSON")
    parser.add_argument(
        "--strict-inline-order",
        action="store_true",
        help="Order references by first inline appearance",
    )
    parser.add_argument(
        "--remove-unknown-inline",
        action="store_true",
        help="Remove unknown inline PMID tokens instead of leaving them in place",
    )
    parser.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="Fail if any unknown inline PMID tokens are found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run_pipeline(
            input_path=args.input,
            refs_path=args.refs,
            output_path=args.output,
            report_path=args.report,
            strict_inline_order=args.strict_inline_order,
            remove_unknown_inline=args.remove_unknown_inline,
            fail_on_unknown=args.fail_on_unknown,
        )
    except Exception as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
