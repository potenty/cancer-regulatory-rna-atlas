# Project overview

## Cancer Regulatory RNA Atlas (CRRA)

*An evidence-based resource for exploring noncoding RNA regulation in human cancer.*

## Purpose

Research on regulatory noncoding RNAs in cancer is spread across databases that each cover one RNA class and each use their own notion of evidence. A miRNA–target interaction supported by a mutated-reporter assay and a lncRNA–disease link supported by a single expression correlation are both commonly listed as "interactions."

CRRA organizes published findings for several RNA classes under **one evidence framework**, so that the strength of support for each record is visible and comparable.

CRRA contains no original discoveries. Its contribution is organization and explicit evidence labelling.

## Scope

**RNA classes:** microRNAs, long noncoding RNAs, enhancer RNAs, and other regulatory noncoding RNAs where evidence exists (circular RNAs, pseudogene transcripts, snoRNA host genes).

**Organism:** *Homo sapiens*. Records resting on a non-human orthologue say so.

**Relationships:** RNA → target gene, RNA → cancer type, RNA → publication, plus upstream regulation of the RNA where a source reports it.

## Questions CRRA is built to help answer

- Which regulatory RNAs are associated with which cancer types?
- Which genes do they regulate, and by what mechanism as reported?
- Which relationships have direct experimental support, and which rest on prediction or correlation alone?
- Which relationships recur across cancer types?
- Where are the gaps — RNA classes, cancer types, or evidence tiers that are thinly covered?

The last question is why evidence class is a first-class field rather than a footnote. A gap in strong evidence is itself a finding about the field.

## Components

**A. Database** — four linked CSV tables (`database/`) plus an Excel workbook, covering RNA records, interactions, cancer associations, and publications. See `data_dictionary.md`.

**B. Website** — a static site (`website/`) for searching and filtering records, with evidence class shown on every row and every source link resolvable.

**C. Research foundation** — once coverage is wide enough, the curated tables can support independent computational work on cross-cancer regulatory patterns. Not a v0.1 goal, and gated on the sampling-bias limitation in `limitations.md`.

## Principles

1. **Accuracy before coverage.** A smaller traceable set beats a larger uncertain one. Numerical targets never justify a weaker record.
2. **Nothing from memory.** Every identifier and citation comes from a lookup performed during curation.
3. **The weaker class wins.** Where a source is ambiguous about method, the lower evidence class is recorded and the ambiguity noted.
4. **Missing is recorded as missing** — never as zero, never as a negative finding.
5. **Attribution is preserved.** Every record names its source and links to it.
6. **No unsupported mechanism.** CRRA does not chain findings into pathways that no source states.
7. **No borrowed authority.** No institutional affiliation or endorsement is claimed.

## Status and roadmap

v0.1 is an early prototype. Current state, record counts and outstanding problems are in `PROJECT_STATUS.md`; known weaknesses are in `limitations.md`.

Planned, roughly in order:

1. Full-text review to firm up provisional evidence classes.
2. Documented access to the remaining databases in `source_registry.md`, with licence terms recorded first.
3. Wider cancer-type and RNA-class coverage, with the sampling bias tracked rather than ignored.
4. Pathway annotation, drawn from a pathway database rather than inferred.
5. Interactive network visualization.
6. Independent cross-cancer analysis, only once coverage supports it.

## Repository layout

```
website/          Static site; open website/index.html
database/         CSV tables + master_database.xlsx
documentation/    This file, methodology, source registry, data dictionary, limitations
quality_control/  Duplicate audit, verification report, raw source-check records
scripts/          Build and QC scripts
PROJECT_STATUS.md Session-by-session status
```
