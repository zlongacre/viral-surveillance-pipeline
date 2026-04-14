#!/usr/bin/env python3
"""
Tests for the surveillance report agent.
Validates data parsing and prompt building without requiring Ollama.
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.report_agent.prompt_templates import (
    SYSTEM_PROMPT,
    SURVEILLANCE_REPORT_TEMPLATE,
    QC_SUMMARY_TEMPLATE
)
from src.report_agent.report_agent import (
    parse_lineage_distribution,
    parse_qc_summary,
    extract_notable_mutations,
    build_prompt
)


def make_mock_nextclade():
    """Create minimal mock Nextclade dataframe for testing."""
    return pd.DataFrame({
        'seqName': ['seq1', 'seq2', 'seq3', 'seq4', 'seq5'],
        'clade': ['25C', '25C', '24H', '25B', '25C'],
        'Nextclade_pango': ['XFG.1', 'XFG.1', 'KP.3.1', 'XEC.4', 'XFG.2'],
        'totalSubstitutions': [152, 148, 145, 160, 150],
        'totalDeletions': [68, 70, 65, 72, 69],
        'totalInsertions': [12, 12, 11, 13, 12],
        'totalMissing': [0, 2, 1, 0, 3],
        'totalFrameShifts': [0, 0, 0, 0, 0],
        'totalAminoacidDeletions': [17, 18, 16, 19, 17],
        'qc.overallScore': [0, 2.5, 1.2, 4.3, 0],
        'coverage': [0.998, 0.997, 0.999, 0.996, 0.998],
        'aaSubstitutions': [
            'S:F456L,S:K444R,S:N487D',
            'S:F456L,S:R346T',
            'S:L452R,S:E484K',
            'S:N501Y,S:P681R',
            'S:F456L,S:K444R'
        ]
    })


def make_mock_qc():
    """Create minimal mock QC dataframe for testing."""
    return pd.DataFrame({
        'sequence_id': ['seq1', 'seq2', 'seq3', 'seq4', 'seq5'],
        'length': [29800, 29790, 29785, 29795, 29800],
        'n_count': [0, 2, 1, 0, 3],
        'n_percent': [0.0, 0.01, 0.0, 0.0, 0.01],
        'pass_qc': ['PASS', 'PASS', 'PASS', 'PASS', 'PASS']
    })


def test_lineage_distribution():
    """Test lineage parsing produces correct output."""
    df = make_mock_nextclade()
    summary, counts = parse_lineage_distribution(df)

    assert 'XFG.1' in summary, "XFG.1 should appear in summary"
    assert counts['XFG.1'] == 2, "XFG.1 should have count of 2"
    print("PASS: test_lineage_distribution")


def test_qc_summary():
    """Test QC summary produces correct pass rate."""
    df = make_mock_qc()
    summary = parse_qc_summary(df)

    assert '100.0%' in summary, "All sequences should pass QC"
    assert '5' in summary, "Total should be 5"
    print("PASS: test_qc_summary")


def test_notable_mutations():
    """Test escape mutation detection."""
    df = make_mock_nextclade()
    mutations = extract_notable_mutations(df)

    assert 'S:F456L' in mutations, "S:F456L should be flagged"
    assert 'S:K444R' in mutations, "S:K444R should be flagged"
    print("PASS: test_notable_mutations")


def test_prompt_building():
    """Test full prompt builds without errors."""
    nextclade_df = make_mock_nextclade()
    qc_df = make_mock_qc()

    prompt = build_prompt(nextclade_df, qc_df)

    assert 'SARS-CoV-2' in prompt, "Pathogen should be in prompt"
    assert 'XFG' in prompt, "Lineage should be in prompt"
    assert len(prompt) > 100, "Prompt should have meaningful content"
    print("PASS: test_prompt_building")


def test_system_prompt():
    """Test system prompt is properly defined."""
    assert len(SYSTEM_PROMPT) > 50, "System prompt should have content"
    assert 'virologist' in SYSTEM_PROMPT.lower(), "Should reference virology expertise"
    print("PASS: test_system_prompt")


if __name__ == '__main__':
    print("Running surveillance report agent tests...\n")

    tests = [
        test_system_prompt,
        test_lineage_distribution,
        test_qc_summary,
        test_notable_mutations,
        test_prompt_building,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} — {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)