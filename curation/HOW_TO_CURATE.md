# How to add records

## The loop

1. Open `quality_control/night1_source_checks/abstract_notes.md` — the notes for each paper.
2. Add a row to `curation/interactions.tsv` (or `cancer_associations.tsv`).
3. Run:

```bash
python3 scripts/compile_curation.py && python3 scripts/qc.py && python3 scripts/build.py
```

4. Open `website/index.html` to see the rows.

If a row is malformed the compiler writes nothing and names the bad row. You cannot
silently corrupt the tables.

## Row format — interactions.tsv

Fields separated by `|` (tabs also work). Order:

```
rna_name | target_name | target_gene_id | cancer_type | interaction_type |
regulatory_effect | evidence_class | experimental_method | supporting_pmid | notes
```

Example:

```
MIR21|PDCD4||Colorectal cancer|mRNA target repression|represses|Direct experimental|3'UTR luciferase reporter, abolished by target-site mutation|17968323|
```

- `rna_name` must match an `official_name` in `database/rna_records.csv`.
- `target_gene_id` — leave empty to resolve automatically; put `-` if the target is a
  protein complex with no single gene.
- `cancer_type` — write `Not specified in abstract` if the source names none. Never guess.
- `evidence_class` — exactly one of:
  - `Direct experimental`
  - `Experimental functional`
  - `Computational prediction`
  - `Literature association`
- Trailing `|` with nothing after it means an empty notes field. That is fine.

## Row format — cancer_associations.tsv

For RNA-cancer relationships with no specific gene target.

```
rna_name | cancer_type | direction | clinical_association | evidence_class |
cohort_description | supporting_pmid | notes
```

`direction` is `upregulated`, `downregulated`, `deleted`, `amplified` or empty.

## Choosing the evidence class

| If the abstract... | Class |
|---|---|
| names a binding test — reporter with site mutation, pulldown, RIP, CLIP | Direct experimental |
| says the RNA was perturbed and the target changed, no binding test named | Experimental functional |
| reports prediction, sequence complementarity or statistical association only | Computational prediction |
| reports expression, prognosis or genomic alteration with no causal test | Literature association |

When a source asserts a direct target but names no assay, record the **weaker** class and
say so in `notes`. That rule is in `documentation/methodology.md`; keeping to it is what
makes the evidence column mean anything.

## Checklist

`curation/TODO_checklist.md` lists the papers with no row yet.
