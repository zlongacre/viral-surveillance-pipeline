#!/usr/bin/env python3
"""
Prompt templates for the surveillance report agent.
Mirrors the briefing format used in production surveillance programs.
"""

SYSTEM_PROMPT = """You are an expert virologist and genomic epidemiologist 
specializing in viral variant surveillance. You analyze sequencing data and 
produce clear, actionable surveillance reports for scientific and executive 
audiences. Your reports are concise, evidence-based, and highlight 
epidemiological significance."""

SURVEILLANCE_REPORT_TEMPLATE = """
You are analyzing genomic surveillance data for {pathogen}.
Generate a structured surveillance report based on the following pipeline outputs.

## Input Data Summary
- Total sequences analyzed: {total_sequences}
- Date range: {date_range}
- Geographic scope: {geography}

## Lineage Distribution
{lineage_summary}

## QC Summary
{qc_summary}

## Top Circulating Lineages
{top_lineages}

## Notable Mutations
{notable_mutations}

Generate a surveillance report with the following sections:
1. Executive Summary (2-3 sentences, suitable for leadership briefing)
2. Dominant Lineages (what is circulating and at what frequency)
3. Emerging Variants (any low-frequency lineages to watch)
4. Quality Assessment (data confidence level)
5. Recommendations (antigen selection implications if relevant)

Be specific, cite the data provided, and flag anything that warrants 
immediate attention. Write for a scientific audience but keep it actionable.
"""

QC_SUMMARY_TEMPLATE = """
- Total sequences: {total}
- Sequences passing QC: {passing} ({pass_rate}%)
- Average genome coverage: {avg_coverage}%
- Average N content: {avg_n_content}%
"""