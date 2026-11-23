# Source registry

Status of the nine resources named in the Night 1 brief.

**Access status** records whether CRRA actually reached the resource during curation. Only resources marked **Used** contributed records to v0.1. Descriptions of resources marked *Not yet accessed* are background, not verification, and must be confirmed before they are relied on.

---

## PubMed / NCBI E-utilities — **Used**

- **Provides:** publication metadata (title, authors, journal, year, DOI), abstracts, MeSH terms, and publication-type flags including `Retracted Publication`, `Expression of Concern` and `Erratum`.
- **RNA categories:** all, indirectly — it indexes the literature rather than RNAs.
- **Evidence type:** primary literature. Evidence class must be read out of each paper; PubMed does not assign one.
- **Identifiers:** PMID, PMCID, DOI.
- **Access:** `https://pubmed.ncbi.nlm.nih.gov/` · API `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` · docs `https://www.ncbi.nlm.nih.gov/books/NBK25501/`
- **Used for:** every publication record in v0.1, and all retraction screening.
- **Limitations:** abstracts often assert a "direct target" without naming the assay, so abstract-only curation systematically understates method detail. Retraction flags can lag publisher notices.
- **Terms:** US Government work, not subject to copyright; E-utilities usage policy caps request rates and asks for a tool/email identifier. Abstract *text* remains under publisher copyright, so CRRA stores paraphrases only.

## NCBI Gene — **Used**

- **Provides:** stable gene records, official symbols, aliases, chromosome, description, for RNA genes and protein-coding targets alike.
- **RNA categories:** miRNA, lncRNA, circRNA host genes, pseudogenes; eRNAs mostly absent.
- **Evidence type:** nomenclature, not interaction evidence.
- **Identifiers:** NCBI Gene ID.
- **Access:** `https://www.ncbi.nlm.nih.gov/gene/`
- **Used for:** every `stable_identifier` and `target_gene_id` in v0.1.
- **Limitations:** several eRNAs named in primary papers have no Gene record at all. Those CRRA records carry an empty identifier by design.
- **Terms:** US Government work, not subject to copyright.

## Europe PMC — **Partially used, then unavailable**

- **Provides:** publication metadata and full-text search across PubMed plus preprints and patents; a REST API with structured author lists.
- **Identifiers:** PMID, PMCID, DOI.
- **Access:** `https://europepmc.org/` · API `https://www.ebi.ac.uk/europepmc/webservices/rest/` · docs `https://europepmc.org/RestfulWebService`
- **What happened:** the REST API returned valid results for an initial batch, then returned `HTTP 503 Service Temporarily Unavailable` for subsequent requests, consistent with rate limiting. Curation moved to NCBI E-utilities.
- **Cross-check found:** for one paper (PMID 20393566) the Europe PMC author list repeated an author name that PubMed lists once. PubMed was treated as authoritative. A single discrepancy is not a general verdict on either source, but it is a reason to prefer one source per field rather than mixing them.
- **Limitations:** rate limits are not documented precisely enough to plan around; no fixed quota is published.
- **Terms:** metadata available under the EMBL-EBI terms of use; individual full texts carry their own licences.

## miRTarBase — *Not yet accessed*

- **Expected to provide:** curated miRNA–target interactions with the supporting assay recorded per interaction, which maps unusually well onto CRRA's evidence classes.
- **Why it matters:** it is the main reason miRNA coverage in any atlas outpaces other RNA classes.
- **Access to confirm:** base URL, current release, and download format.
- **Known concern:** redistribution is restricted and academic-use conditions apply. **Terms must be read before any miRTarBase-derived record is included, and certainly before any public release.**

## ENCORI / starBase — *Not yet accessed*

- **Expected to provide:** miRNA–target and RNA–RNA interactions, mixing CLIP-supported interactions with algorithmic predictions.
- **Curation requirement:** predicted and CLIP-supported interactions must be separated into `Computational prediction` and `Direct experimental` respectively. Importing without that split would violate CRRA's core rule.
- **Access to confirm:** current URL and whether programmatic access is offered.

## RNAcentral — *Not yet accessed*

- **Expected to provide:** stable identifiers (URS accessions) for noncoding RNA sequences across member databases.
- **Why it matters:** the most likely route to identifiers for RNAs that NCBI Gene does not cover.
- **Access attempted:** `https://rnacentral.org/` — the workspace network refused the connection (see *Access constraints* below).
- **Terms:** generally open; to be confirmed.

## LncBook — *Not yet accessed*

- **Expected to provide:** a curated human lncRNA knowledgebase with annotation and disease association.
- **Access to confirm:** current URL, release, and licence.

## LncRNADisease — *Not yet accessed*

- **Expected to provide:** lncRNA–disease associations, experimentally supported and predicted.
- **Curation requirement:** as with ENCORI, the two must not be merged.
- **Access to confirm:** current URL and licence.

## GEO — *Not yet accessed*

- **Expected to provide:** raw and processed expression datasets, not curated interactions.
- **Relevance:** out of scope for v0.1, which records published relationships rather than re-analysing data. Relevant only if CRRA later does its own analysis.
- **Identifiers:** GSE / GSM / GPL accessions.
- **Access:** `https://www.ncbi.nlm.nih.gov/geo/`

---

## Access constraints encountered

- **Workspace network:** the curation environment's egress allowlist refused direct connections to `eutils.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `rnacentral.org` and `rest.genenames.org`. All lookups were therefore made through the browser instead.
- **Europe PMC:** rate limited mid-session, as above.
- **Bulk downloads:** no database dump was downloaded. Every v0.1 record came from an individual API response.

## Rules carried forward

1. Record each source's redistribution terms **before** importing from it, not after.
2. Never merge a source's predicted and experimental tiers into one evidence class.
3. One source per field. Where sources disagree, record the disagreement rather than silently picking one.
4. If a source is unreachable, document it here and move on. Do not substitute memory for a lookup.
