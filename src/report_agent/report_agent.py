#!/usr/bin/env python3
"""
Surveillance report agent.
Reads pipeline outputs and generates AI-powered surveillance summaries.
Phase 3 of the viral genomic surveillance pipeline.
"""

import pandas as pd
import json
import argparse
import os
from datetime import datetime
from collections import Counter
from src.report_agent.prompt_templates import SYSTEM_PROMPT, SURVEILLANCE_REPORT_TEMPLATE, QC_SUMMARY_TEMPLATE


def load_nextclade_results(filepath):
    """Load and parse Nextclade TSV output."""
    df = pd.read_csv(filepath, sep='\t')
    print(f"Loaded {len(df)} sequences from Nextclade output")
    return df


def load_qc_report(filepath):
    """Load QC report from pipeline."""
    df = pd.read_csv(filepath, sep='\t')
    return df


def parse_lineage_distribution(df):
    """Calculate lineage frequencies from Nextclade output."""
    lineage_col = 'Nextclade_pango' if 'Nextclade_pango' in df.columns else 'clade'
    counts = df[lineage_col].value_counts()
    total = len(df)

    distribution = []
    for lineage, count in counts.head(20).items():
        pct = round((count / total) * 100, 1)
        distribution.append(f"  {lineage}: {count} sequences ({pct}%)")

    return "\n".join(distribution), counts


def parse_qc_summary(df):
    """Summarize QC metrics."""
    total = len(df)
    passing = len(df[df['pass_qc'] == 'PASS']) if 'pass_qc' in df.columns else total
    pass_rate = round((passing / total) * 100, 1)
    avg_coverage = round(df['n_percent'].mean(), 2) if 'n_percent' in df.columns else 'N/A'

    return QC_SUMMARY_TEMPLATE.format(
        total=total,
        passing=passing,
        pass_rate=pass_rate,
        avg_coverage='N/A',
        avg_n_content=avg_coverage
    )


def extract_notable_mutations(df):
    """Extract spike mutations of interest from Nextclade output."""
    if 'aaSubstitutions' not in df.columns:
        return "No mutation data available"

    # Known immune escape mutations to flag
    escape_mutations = [
        'S:F456L', 'S:K444R', 'S:N487D', 'S:R346T',
        'S:L452R', 'S:E484K', 'S:N501Y', 'S:P681R'
    ]

    flagged = []
    for mutation in escape_mutations:
        count = df['aaSubstitutions'].str.contains(
            mutation, na=False).sum()
        if count > 0:
            pct = round((count / len(df)) * 100, 1)
            flagged.append(f"  {mutation}: {count} sequences ({pct}%)")

    if flagged:
        return "\n".join(flagged)
    return "No high-priority escape mutations detected"


def build_prompt(nextclade_df, qc_df, pathogen="SARS-CoV-2"):
    """Build the complete prompt for the LLM."""
    lineage_summary, counts = parse_lineage_distribution(nextclade_df)
    qc_summary = parse_qc_summary(qc_df)
    notable_mutations = extract_notable_mutations(nextclade_df)

    top_lineages = "\n".join([
        f"  {k}: {v} sequences"
        for k, v in counts.head(5).items()
    ])

    prompt = SURVEILLANCE_REPORT_TEMPLATE.format(
        pathogen=pathogen,
        total_sequences=len(nextclade_df),
        date_range=datetime.now().strftime("%Y-%m"),
        geography="USA (NCBI submissions)",
        lineage_summary=lineage_summary,
        qc_summary=qc_summary,
        top_lineages=top_lineages,
        notable_mutations=notable_mutations
    )

    return prompt


def generate_report_ollama(prompt, model="llama3.2"):
    """Generate report using Ollama (local, free)."""
    import requests

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False
        }
    )

    if response.status_code == 200:
        return response.json()['response']
    else:
        raise Exception(f"Ollama error: {response.status_code}")


def save_report(report, outdir):
    """Save report to output directory."""
    os.makedirs(outdir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{outdir}/surveillance_report_{timestamp}.txt"

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered surveillance report generator')
    parser.add_argument('--nextclade', required=True,
                        help='Nextclade TSV output')
    parser.add_argument('--qc', required=True,
                        help='QC report from pipeline')
    parser.add_argument('--outdir', default='data/output',
                        help='Output directory for reports')
    parser.add_argument('--model', default='llama3.2',
                        help='Ollama model to use')
    args = parser.parse_args()

    # Load pipeline outputs
    nextclade_df = load_nextclade_results(args.nextclade)
    qc_df = load_qc_report(args.qc)

    # Build prompt
    print("\nBuilding surveillance prompt...")
    prompt = build_prompt(nextclade_df, qc_df)

    # Generate report
    print("Generating AI surveillance report...")
    report = generate_report_ollama(prompt, model=args.model)

    # Print and save
    print("\n" + "="*60)
    print(report)
    print("="*60)

    save_report(report, args.outdir)


if __name__ == '__main__':
    main()