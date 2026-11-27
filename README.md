# cancer-regulatory-rna-atlas
An independent, evidence-based atlas of regulatory noncoding RNA interactions in human cancer.

---

## What this is

A method for grading the strength of published evidence behind noncoding RNA–cancer claims, and a
pilot applying it to 131 curated records across four RNA classes.

It is **not** a comprehensive database and does not try to be. For microRNA–target interactions,
[miRTarBase](https://mirtarbase.cuhk.edu.cn/) holds over 400,000 curated entries with its own
validation tiers and is better than this in every way that size matters. What no existing
resource does is apply **one** evidence rubric across miRNA, lncRNA, eRNA and circRNA, so that
the classes can be compared on the same scale. That is the gap this pilot was built to test.

## The result

Of 57 interaction rows whose evidence class was checked against the paper's methods section,
**27 (47%) were supported by a direct binding assay** — a reporter with mutated target sites,
RIP, CLIP, ChIRP, EMSA or a pulldown. The rest reported that perturbing the RNA changed the
target, without demonstrating that they bind.

Broken down by RNA class:

| RNA class | Verified rows | Direct evidence | |
|---|---|---|---|
| miRNA | 24 | 13 | 54% |
| lncRNA | 18 | 10 | 56% |
| eRNA | 11 | 4 | 36% |
| circRNA | 3 | 0 | 0% |

**These classes cannot be distinguished at this sample size.** miRNA and lncRNA are effectively
identical; eRNA looks lower but 4 of 11 is well within chance of the others. The question the
pilot was built to ask — whether the evidence base is weaker for some RNA classes than others —
is not answered here, and would need roughly 50–100 verified rows per class before a difference
of that size could show up.

That is the honest finding: **the method works, the sample is too small to use it.**

## Contents

| | |
|---|---|
| RNA records | 58 — 32 miRNA, 15 lncRNA, 7 eRNA, 2 circRNA, 1 pseudogene transcript, 1 snoRNA host gene |
| Interactions | 94, each with an evidence class and a resolvable citation |
| Cancer associations | 37 across 10 cancer types |
| Publications | 49, all metadata verified against PubMed |
| Full texts read | 28 papers; 8 more are paywalled and recorded as unread |

## Evidence classes

| Class | Requirement |
|---|---|
| **Direct experimental** | A binding test is reported — reporter with site mutation, pulldown, RIP, CLIP, ChIRP, EMSA |
| **Experimental functional** | The RNA was perturbed and the target changed, with no binding evidence recorded |
| **Computational prediction** | Algorithm, sequence complementarity or statistical association only |
| **Literature association** | Expression, prognostic or genomic correlation, with no causal test |

Two rules do most of the work. Where a source asserts a direct target without naming the assay,
the **weaker** class is recorded. And a result shown for one family member is never extended to
another on the strength of a shared seed sequence — that is a prediction, not an experiment.

Every row also carries `class_source`, recording whether its class was established from a methods
section or only from an abstract. Rows of the second kind are marked **unverified** on the site.

## What went wrong, and was caught

Kept here because the corrections are the most informative part of the project.

- **Ten candidate PMIDs** turned out to belong to unrelated papers. All ten were discarded rather
  than corrected by guesswork; each would have become a fabricated citation.
- **One retracted paper** was caught by PubMed publication-type flags and excluded.
- **Two seed rows** were classed `Direct experimental` on authors' wording alone, breaking the
  project's own rule, and were then copied as the pattern for later curation. Both downgraded.
- **let-7a–HMGA2** was downgraded after full-text review: the paper's binding assay used a
  let-7b/let-7e mixture, so extending it to let-7a rested on seed-sharing.
- **A script bug** would have erased 31 review marks the second time it ran.

None of these were caught by the automated checks, which passed throughout. Every one was found
by a person reading output and asking whether a number looked right. **Automated checks catch
malformed data; they do not catch wrong data.**

## Using it

The site is static — open `website/index.html` in a browser, no server needed.

```bash
python3 scripts/compile_curation.py   # curation/*.tsv -> database/*.csv
python3 scripts/build.py              # CSVs -> website data + master_database.xlsx
python3 scripts/qc.py                 # validation; exit 1 on error
```

## Layout

```
website/            Static site: explorer, network view, methodology
database/           CSV tables + master_database.xlsx
documentation/      Overview, methodology, data dictionary, source registry, limitations
quality_control/    Verification report, duplicate audit, full-text access log, raw source checks
curation/           Hand-curated TSVs and the curation guide
scripts/            Build, QC and curation tooling
```

Read [`documentation/limitations.md`](documentation/limitations.md) before using the data, and
[`quality_control/verification_report.md`](quality_control/verification_report.md) for what was
and was not checked.

## Status

Complete as a pilot. Extending it to a finding would need: more verified rows per class, library
access for the 8 paywalled papers, and the remaining databases in
[`source_registry.md`](documentation/source_registry.md) with their licence terms read first.

An independent project. No institutional affiliation, sponsorship or endorsement is claimed, and
nothing here is medical advice.
