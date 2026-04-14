#!/bin/bash -ue
python3 -c "
from Bio import SeqIO
import sys

records = list(SeqIO.parse('sars_cov2_test.fasta', 'fasta'))
with open('qc_report.txt', 'w') as f:
    f.write('sequence_id\tlength\tn_percent\tpass_qc\n')
    for rec in records:
        length = len(rec.seq)
        n_count = rec.seq.upper().count('N')
        n_pct = round((n_count / length) * 100, 2)
        pass_qc = 'PASS' if length > 25000 and n_pct < 5 else 'FAIL'
        f.write(f'{rec.id}\t{length}\t{n_count}\t{n_pct}\t{pass_qc}\n')
    f.write(f'\nTotal sequences: {len(records)}\n')
"
