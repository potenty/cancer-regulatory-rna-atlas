# Methodology

## What CRRA is

CRRA is a curated index of **published** findings about regulatory noncoding RNAs in human cancer. It contains no original experimental results and no original analyses. Every record points back to a source publication or database entry.

## Record provenance

Night 1 records were curated by hand. Two official sources were used for every record:

1. **PubMed E-utilities** (`eutils.ncbi.nlm.nih.gov`) — publication metadata (title, author list, journal, year, DOI, publication-type flags) and abstracts.
2. **NCBI Gene** — stable gene identifiers for every RNA and target gene symbol.

No record was entered from memory. Where a candidate identifier did not resolve to the expected paper, the candidate was discarded rather than corrected by guesswork. Discarded candidates are listed in `quality_control/night1_source_checks/`.

## Evidence classification

Each interaction and cancer association carries exactly one class.

| Class | Requirement |
|---|---|
| **Direct experimental** | The publication reports a physical or direct interaction test: reporter assay with binding-site mutation, RNA pulldown, RIP, CLIP, or equivalent. |
| **Experimental functional** | The RNA was perturbed experimentally and the target or phenotype changed, but no direct-binding evidence is recorded in the source we read. |
| **Computational prediction** | Inferred by algorithm, sequence complementarity, or statistical association only. |
| **Literature association** | Expression correlation, clinical or prognostic association, or genomic alteration reported, with no causal test. |

### Rules applied

- **The class reflects what the source we read actually states.** Night 1 classes were assigned from PubMed abstracts, not full texts. Where an abstract asserts a target relationship without naming the assay, the record is classed **Experimental functional**, which is the weaker claim, and the limitation is recorded in the record's notes.
- A prediction is never recorded as experimentally validated.
- Missing information is recorded as missing. It is never recorded as a negative finding, and never filled in by inference.
- Where authors state a direct target but the abstract does not name the method, the record says so in its method field rather than naming an assay that was not reported.

Because Night 1 classes rest on abstracts, they are **provisional**. Upgrading them requires full-text review, which is tracked as outstanding work in `PROJECT_STATUS.md`.

## Retraction and integrity screening

Parts of the noncoding-RNA literature, particularly lncRNA "sponge" papers from roughly 2016–2020, have been affected by retractions and paper-mill output. Every candidate publication was therefore checked for PubMed publication-type flags (`Retracted Publication`, `Expression of Concern`, `Erratum`).

- Papers flagged as retracted were **excluded**, and the exclusion recorded.
- Papers with an erratum or a published comment were **kept**, with the flag recorded on the publication record so a reader can follow it.

This screening used PubMed flags only. It is not a substitute for checking Retraction Watch, which is outstanding work.

## Known methodological limits

- Abstract-level curation (see above).
- Enhancer RNAs have no equivalent of miRTarBase, so eRNA coverage is thin and skewed toward recent primary papers. This is a real gap in the field, not only in CRRA.
- Several eRNAs have no stable identifier in any nomenclature database. Those records carry the name used by the publication and an explicitly empty identifier field.
- Cancer type is recorded as the source states it. Where an abstract reports only cell-line work without naming a tumour type, the field reads `Not specified in abstract` rather than a guessed type.

## Licensing

Source databases differ in redistribution terms. Each entry in `source_registry.md` records the terms found for that source. Any future public release of CRRA data must be checked against those terms first.
