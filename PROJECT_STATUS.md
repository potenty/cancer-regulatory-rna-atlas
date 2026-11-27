# PROJECT_STATUS

**Version:** v1.0 — complete as a pilot
**Last updated:** 2026-11-26

---

## State

| | |
|---|---|
| RNA records | 58 — 32 miRNA, 15 lncRNA, 7 eRNA, 2 circRNA, 1 pseudogene transcript, 1 snoRNA host gene |
| Interactions | 94 — 28 Direct experimental, 64 Experimental functional, 2 Literature association |
| Cancer associations | 37 across 10 cancer groups |
| Publications | 49, metadata verified against PubMed |
| Full texts read | 28 papers; 8 paywalled and recorded as unread |

QC passes with 0 errors and 1 warning — the single `Direct experimental` row whose paper could
not be read. Workbook recalculates with 0 formula errors. Site loads with no console errors.

## Result

Of 57 interaction rows whose class was checked against a methods section, 27 (47%) were
supported by a direct binding assay.

| RNA class | Verified | Direct | Share |
|---|---|---|---|
| miRNA | 24 | 13 | 54% |
| lncRNA | 18 | 10 | 56% |
| eRNA | 11 | 4 | 36% |
| circRNA | 3 | 0 | 0% |

**The classes cannot be distinguished at this sample size.** The question the pilot was built to
ask is not answered. Roughly 50–100 verified rows per class would be needed.

## What was built

- **Evidence framework** — four classes, with the weaker class recorded wherever a source asserts
  a direct target without naming the assay, and family results never extended on shared seeds.
- **`class_source`** — records whether each class came from a methods section or an abstract, so
  unverified strong claims are visible rather than buried in notes.
- **Curation pipeline** — `curation/*.tsv` → `compile_curation.py` → CSVs → `build.py` → site and
  workbook, with `qc.py` validating duplicates, identifiers, foreign keys, evidence vocabulary,
  cancer vocabulary and unverified Direct rows.
- **Website** — RNA and interaction explorers, a force-directed network, publications and a
  methodology page, all static and offline-capable.
- **Documentation** — overview, methodology, data dictionary, source registry, limitations, and a
  verification report recording what was and was not checked.

## Corrections made

The most informative part of the record. None were caught by the automated checks.

| What | Outcome |
|---|---|
| 10 candidate PMIDs belonged to unrelated papers | Discarded, not corrected by guesswork |
| 1 retracted paper (19524507) | Excluded via PubMed flags |
| 2 seed rows classed Direct on authors' wording | Downgraded; they had been copied as the pattern |
| let-7a–HMGA2 | Downgraded — assay used a let-7b/e mixture, not let-7a |
| Cancer-type filter defects | Subtypes split their parent; compound cells unreachable |
| Interaction table 15,154px tall | Paginated at 25 rows |
| `check_fulltext_access.py` | Would have erased 31 review marks on its second run |
| Review queue | Built from provisional rows only, so Direct rows were never audited |

## Outstanding, if ever extended

1. **More verified rows per class** — the only route to a finding.
2. **Library access** for 8 paywalled papers, including Gregory 2008 (12 rows).
3. **`main_finding`** empty for all 49 publications.
4. **~11 Gregory/Park association rows**, decided to include, not yet entered.
5. **Six databases unvisited** — miRTarBase, ENCORI, RNAcentral, LncBook, LncRNADisease, GEO.
   Licence terms must be read before any import. The schema already supports a bulk import kept
   separate from hand-verified rows via `class_source`.
6. **Retraction Watch** not checked; PubMed flags alone are necessary but not sufficient.
7. **31 rows in family papers** are structurally un-upgradeable — a property of the
   family-expansion convention, not of the literature.

## Rebuilding

```bash
python3 scripts/compile_curation.py
python3 scripts/build.py
python3 scripts/qc.py
python3 scripts/recalc.py database/master_database.xlsx
open website/index.html
```

`derive_tables.py` only needs running if the RNA and publication tables are lost; it rebuilds
them from the verification records in `quality_control/night1_source_checks/`.

## Continuity

The GitHub repository is the only persistent store. Start any new session by cloning it and
reading this file.
