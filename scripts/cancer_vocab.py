#!/usr/bin/env python3
"""Controlled vocabulary for cancer types.

`cancer_type` always keeps the source's own wording - that is the record of what the
publication said. `cancer_group` is a normalised term derived from it, so filters and
counts can group what belongs together without rewriting any source wording.

A compound cell ("Hepatocellular carcinoma; bladder carcinoma") yields several groups.
Nothing here merges distinct diseases: NSCLC maps under lung cancer because it is a
subtype of it, not because the names look similar.
"""

# source term (lowercased) -> normalised group
GROUPS = {
    "breast cancer": "Breast cancer",
    "prostate cancer": "Prostate cancer",
    "ovarian cancer": "Ovarian cancer",
    "colorectal cancer": "Colorectal cancer",
    "hepatocellular carcinoma": "Liver cancer",
    "bladder carcinoma": "Bladder cancer",
    "lung cancer": "Lung cancer",
    "non-small cell lung cancer": "Lung cancer",
    "glioblastoma": "Brain cancer",
    "pancreatic cancer": "Pancreatic cancer",
    "chronic lymphocytic leukemia": "Leukemia",
}

UNSPECIFIED = "Not specified"


def groups_for(cancer_type):
    """Return the normalised groups for a cancer_type cell, as a sorted list."""
    raw = (cancer_type or "").strip()
    if not raw or "not specified" in raw.lower():
        return [UNSPECIFIED]
    out = []
    for part in [p.strip() for p in raw.split(";") if p.strip()]:
        g = GROUPS.get(part.lower())
        if g is None:
            # Unmapped term: keep it as its own group rather than guessing a parent,
            # and let qc.py report it so the vocabulary gets extended deliberately.
            g = part
        if g not in out:
            out.append(g)
    return sorted(out)


def unmapped(cancer_types):
    """Source terms with no entry in GROUPS - surfaced by QC, never auto-merged."""
    missing = set()
    for ct in cancer_types:
        raw = (ct or "").strip()
        if not raw or "not specified" in raw.lower():
            continue
        for part in [p.strip() for p in raw.split(";") if p.strip()]:
            if part.lower() not in GROUPS:
                missing.add(part)
    return sorted(missing)
