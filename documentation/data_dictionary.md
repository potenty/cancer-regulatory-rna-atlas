# Data dictionary

Four CSV tables in `database/`. All files are UTF-8 with a header row. Empty string means **not recorded**; it never means zero, absent, or a negative finding.

## `rna_records.csv`

| Column | Meaning |
|---|---|
| `rna_id` | CRRA-local key, e.g. `CRRA-RNA-0001`. Stable within a release only. |
| `official_name` | Preferred symbol, HGNC/miRBase form where one exists. |
| `rna_category` | `miRNA`, `lncRNA`, `eRNA`, `circRNA`, `pseudogene transcript`, `snoRNA host gene`. |
| `alternative_names` | Semicolon-separated synonyms as found in NCBI Gene aliases or the source publication. |
| `stable_identifier` | NCBI Gene ID, prefixed `NCBIGene:`. Empty where no record exists. |
| `identifier_source` | Which database the identifier came from. |
| `organism` | `Homo sapiens` for all Night 1 records. |
| `source_database` | Where the record was curated from. |
| `source_url` | Resolvable URL for that record. |
| `notes` | Curator notes, including why an identifier is empty. |

## `interactions.csv`

| Column | Meaning |
|---|---|
| `interaction_id` | CRRA-local key, e.g. `CRRA-INT-0001`. |
| `rna_id` | Foreign key to `rna_records.csv`. |
| `rna_name` | Denormalised for readability. |
| `target_name` | Target gene, RNA, or protein complex. |
| `target_gene_id` | `NCBIGene:` ID. Empty where the target is a complex, or where the source names no specific gene. |
| `cancer_type` | As stated by the source, or `Not specified in abstract`. |
| `interaction_type` | e.g. `mRNA target repression`, `transcriptional regulation`, `RNA-protein binding`, `miRNA sponging`, `enhancer-promoter activation`. |
| `regulatory_effect` | `represses`, `activates`, `stabilises`, or empty if undocumented. |
| `evidence_class` | One of the four classes in `methodology.md`. |
| `experimental_method` | Assay as named by the source. Where the source asserts a relationship without naming an assay, this records that fact. |
| `supporting_pmid` | PubMed ID. |
| `original_source` | Database or publication the record was curated from. |
| `notes` | Caveats, including why a weaker class was chosen. |

A row with an empty `evidence_class` is invalid and fails QC.

## `cancer_associations.csv`

| Column | Meaning |
|---|---|
| `association_id` | CRRA-local key, e.g. `CRRA-CA-0001`. |
| `rna_id` / `rna_name` | Foreign key and denormalised name. |
| `cancer_type` | As stated by the source. |
| `direction` | `upregulated`, `downregulated`, `deleted`, `amplified`, or empty. |
| `clinical_association` | e.g. `poor prognosis`, `metastasis`, or empty. |
| `evidence_class` | As above. |
| `cohort_description` | Sample counts as the source reports them. Empty if not stated. |
| `supporting_pmid` | PubMed ID. |
| `notes` | Curator notes. |

`direction` and `clinical_association` are independent. An RNA can be recorded as upregulated with no clinical association, and vice versa.

## `publications.csv`

| Column | Meaning |
|---|---|
| `pmid` | PubMed ID, primary key. |
| `doi` | DOI where PubMed records one. |
| `title` | Exactly as PubMed returns it. |
| `authors` | First six authors then `et al.`, as PubMed returns them. |
| `journal` | ISO abbreviation. |
| `year` | Publication year. |
| `cancer_types` | Semicolon-separated. |
| `rna_categories` | Semicolon-separated. |
| `main_finding` | Curator's paraphrase of the abstract. Not a quotation. |
| `pubmed_flags` | Erratum, comment, or expression-of-concern notices. Empty if none. |
| `publication_url` | `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`. |

## Conventions

- Identifiers are prefixed with their namespace (`NCBIGene:7157`) so the source is never ambiguous.
- `main_finding` is always a paraphrase. Source text is not reproduced verbatim.
- Every row in `interactions.csv` and `cancer_associations.csv` must carry a `supporting_pmid`. Rows without one fail QC.
