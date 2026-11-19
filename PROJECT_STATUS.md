# PROJECT_STATUS

**Version:** v0.1-pre (Night 1, in progress, branch `night-1`)
**Last updated:** 2026-11-19

## Done
- Repo inspected (one initial commit, README.md only). README expanded; original title and description kept.
- Folder structure created: website/, database/, documentation/, quality_control/, scripts/.
- Candidate publications checked against PubMed E-utilities (titles, authors, DOIs, publication-type flags). 49 PMIDs confirmed; 11 wrong candidate PMIDs rejected; 1 retracted paper excluded (PMID 19524507).
- Abstracts read and evidence-class notes recorded for all 49.
- NCBI Gene IDs resolved for ~100 RNA and target symbols.
- Raw check files: `quality_control/night1_source_checks/`.

## Not done yet
- CSV tables, Excel workbook, website, documentation set, QC report.

## Source access
- Shell has no network access to PubMed, Europe PMC, NCBI or RNAcentral (proxy refusal).
- Europe PMC REST via browser: worked at first, then returned HTTP 503 (throttling).
- PubMed / NCBI E-utilities via browser: working; this is the main verification route.
- Not yet checked: miRTarBase, ENCORI, RNAcentral, LncBook, LncRNADisease, GEO.

## Next steps
1. Turn the notes in night1_source_checks/ into the four CSV tables.
2. Build the workbook and website from those CSVs.
3. Write the documentation and QC report.
