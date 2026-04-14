# Viral Genomic Surveillance Pipeline

End-to-end NGS pipeline for SARS-CoV-2 and influenza genomic surveillance,
built on production experience running real-time variant monitoring programs.

## What it does

**Phase 1 — Surveillance pipeline (complete)**
- Sequence QC — validates assembled genomes for length and ambiguity content
- Lineage classification — Nextclade clade and Pango lineage assignment
- Processes FASTA inputs from GISAID and NCBI GenBank

**Phase 2 — Variant emergence prediction (in development)**
- Historical lineage frequency tracking from GISAID metadata
- ML model to predict which variants are likely to become dominant
- Trained on known emergence events: Delta, Omicron, XBB, JN.1, XFG

## Results so far
- Pipeline validated on 500 real SARS-CoV-2 sequences (2024-2026)
- 142 distinct lineages identified across XFG, XEC, KP.3, PQ clades
- Random Forest classifier achieving 22.6% CV accuracy across 142 classes
  (baseline random = <1%)

## Stack
Nextflow · Python · Nextclade · BioPython · scikit-learn · DVC

## Quick start
```bash
conda env create -f environment.yml
conda activate surveillance
nextflow run main.nf
python src/lineage_classifier.py --input data/processed/lineages/nextclade.tsv --outdir models/
```

## Data sources
- GISAID (account required)
- NCBI GenBank (open access)

## Status
Active development. Pangolin re-enabled on Linux PC.