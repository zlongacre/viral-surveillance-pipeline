# Viral Genomic Surveillance Pipeline

End-to-end pipeline for SARS-CoV-2 and influenza genomic surveillance.
Built on real-world NGS surveillance experience from production environments.

## What it does
- Sequence QC — validates assembled genomes for length and ambiguity
- Lineage classification — Nextclade clade and Pango lineage assignment
- Phylogenetic analysis — coming soon

## Stack
Nextflow · Python · Nextclade · BioPython · scikit-learn

## Quick start
```bash
conda env create -f environment.yml
conda activate surveillance
nextflow run main.nf
```

## Data sources
- GISAID (account required)
- NCBI GenBank

## Status
Active development. Pangolin re-enabled on Linux PC.