# Limitations

Read this before using CRRA data for anything.

## 1. CRRA is an index, not a discovery

Nothing here is an original finding. Every record restates something already published. CRRA's only contribution is applying one consistent evidence framework across RNA classes that are usually catalogued separately.

CRRA is an independent student project. It carries no institutional affiliation and no scientific endorsement.

## 2. Evidence classes are provisional

Night 1 classes were assigned from **PubMed abstracts, not full texts**. Abstracts routinely say "directly targets" without naming the assay. In those cases CRRA records the weaker class (`Experimental functional`), so some records understate the evidence that exists in the paper. Full-text review is required before any class should be treated as settled.

## 3. Coverage is small and non-random

v0.1 holds on the order of tens of records, chosen because they are well known and traceable. That makes them a convenience sample, biased toward:

- highly cited, older papers for miRNAs and lncRNAs;
- recent primary papers for eRNAs, because nothing older is well catalogued;
- genes and cancer types that attract research attention.

**CRRA cannot be used to estimate how common anything is.** Counts in CRRA reflect curation effort, not biology. An RNA absent from CRRA is not evidence that it is unstudied.

## 3a. Row counts are not finding counts

A row is one RNA-target pair from one publication. Where a paper reports a result for an RNA
family, each member gets a row, so a single abstract can produce five or more. Two miR-200
papers account for 22 of the interaction rows.

Always read the row count against the number of distinct publications behind it. The website
shows both. Treating rows as independent findings would overstate the evidence by roughly a
factor of two in the current data.

## 4. Enhancer RNA coverage is structurally thin

No curated database catalogues eRNA–target interactions the way miRTarBase does for miRNAs. eRNA records therefore come from individual papers, several eRNAs have no stable identifier anywhere, and the naming is inconsistent between labs. This is a genuine gap in the field.

## 5. Retraction screening is incomplete

Candidates were screened for PubMed retraction flags, and flagged papers were excluded. That screening has real limits:

- PubMed flags can lag the publisher's notice.
- Retraction Watch has not been checked.
- Papers that cite retracted work are not flagged.
- An erratum does not mean a paper is unreliable; those records were kept with the flag recorded.

Given the documented integrity problems in parts of the lncRNA literature, treat single-paper lncRNA records as weaker than their evidence class alone suggests.

## 6. Correlation is not causation

`Literature association` records are correlations: expression differences, prognostic associations, genomic alterations. They say nothing about mechanism or direction of causation. An RNA that is upregulated in a tumour may be a driver, a passenger, or a consequence. CRRA does not distinguish these and the source usually cannot either.

## 7. Mechanism claims stop where the source stops

CRRA records the interaction a paper reports. It does not infer downstream consequences, does not chain interactions into pathways, and does not combine two papers into a mechanism neither one states.

## 8. Missing is not negative

An empty field means nothing was recorded. It never means the source tested and found no effect. CRRA holds no negative results, because the literature largely does not publish them.

## 9. Not clinical information

CRRA is a literature index for research purposes. Nothing in it is medical advice, diagnostic information, or a guide to treatment.

## 10. Identifier caveats

- Gene IDs come from NCBI Gene for *Homo sapiens*. Where a source studied a mouse or *C. elegans* orthologue, the record says so in notes.
- `rna_id`, `interaction_id` and `association_id` are local keys, stable within a release only. Do not cite them externally; cite the PMID.
