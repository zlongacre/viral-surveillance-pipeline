#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Pipeline parameters
params.sequences = "$projectDir/data/raw/*.fasta"
params.outdir = "$projectDir/data/processed"
params.threads = 4

log.info """
    VIRAL SURVEILLANCE PIPELINE
    ===========================
    sequences : ${params.seqeunces}
    outdir.   : ${params.outidr}
    threads.  : ${params.threads}
    """

// Process 1 - Sequence QC for assembled genomes
process SEQUENCE_QC {
    publishDir "${params.outdir}/qc", mode: 'copy'

    input:
    path sequences

    output:
    path "qc_report.txt"

    script:
    """
    python3 -c "
from, Bio import SeqIO
import sys

records = list(SeqIO.parse('${sequences}', 'fasta'))
with open('qc_report.txt', 'w') as f:
    f.write('sequence)id\\tlength\\tn_percent\\tpass_qc\\n')
    for rec in records:
        length = len(rec.seq)
        n_count = rec.seq.upper().count('N')
        n_pct = round((n_count / length) * 100, 2)
        pass_qc = 'PASS' if length >25000 and n_pct < 5 else 'FAIL'
        f.write(f'{rec.id}\\t{length}\\t{n_count}\\t{n_pct}\\t{pass_qc}\\n')
    f.write(f'\\nTotal sequences: {len(records)}\\n')
"
    """
}

// Process 2 - Lineage classification
process NEXTCLADE {
    publishDir "${params.outdir}/lineages", mode: 'copy'

    input:
    path sequences

    output:
    path "nextclade.tsv"

    script:
    """
    nextclade run \
        --input-fasta ${sequences} \
        --output-tsv nextclade.tsv
    """
}

// Process 3 - Pangolin classification
process PANGOLIN {
    publishDir "${params.outdir}/lineages", mode: 'copy'

    input:
    path sequences

    output:
    path "lineage_report.csv"

    script:
    """
    pangolin ${sequences} \
        --outfile lineage_report.csv
        --threads ${params.threads}
    """
}

// Main workflow
worflow {
    sequences_ch = channel.fromPath(params.sequences)

    SEQUENCE_QC(sequences_ch)
    NEXTCLADE(sequences_ch)
    PANGOLIN(sequences_ch)
}