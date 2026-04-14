#!/usr/bin/env python3
"""
Download SARS-CoV-2 sequences from NCBI for surveillance analysis.
"""

from Bio import Entrez, SeqIO

Entrez.email = "Zachary.Longacre@gmail.com"

# Search for 500 recent SARS-CoV-2 complete genomes
handle = Entrez.esearch(db="nucleotide",
                        term="SARS-CoV-2 complete genome 2024:2026[PDAT]",
                        retmax=500)
record = Entrez.read(handle)
handle.close()

ids = record["IdList"]
print(f"Found {len(ids)} sequences")

# Fetch in batches of 100
all_seqs = []
for i in range(0, len(ids), 100):
    batch = ids[i:i+100]
    handle = Entrez.efetch(db="nucleotide",
                           id=batch,
                           rettype="fasta",
                           retmode="text")
    all_seqs.append(handle.read())
    handle.close()
    print(f"Downloaded batch {i//100 + 1}")

with open("data/raw/sars_cov2_500.fasta", "w") as f:
    f.write("".join(all_seqs))

print(f"Saved {len(ids)} sequences to data/raw/sars_cov2_500.fasta")