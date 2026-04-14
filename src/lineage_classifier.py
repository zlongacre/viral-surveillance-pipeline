#!/usr/bin/env python3

"""
Lineage classifier for SARS-CoV-2 surveillance data.
Trains an XGBoost model on Nextclade output features to predict lineage.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import argparse
import json
import os

def load_nextclade_output(filepath):
    """Load and parse Nextclade TSV output."""
    df = pd.read_csv(filepath, sep='\t')
    print(f"Loaded {len(df)} sequences from {filepath}")
    print(f"Clades found: {df['clade'].unique()}")
    return df

def extract_features(df):
    """
    Extract ML features from Nextclade output.
    Features: substitution counts, deletion counts, QC scores.
    """
    features = pd.DataFrame()

    # Numeric QC and mutation features
    numeric_cols = [
        'totalSubstitutions',
        'totalDeletions',
        'totalInsertions',
        'totalMissing',
        'totalFrameShifts',
        'totalAnimoacidSubstitutions',
        'totalAminoacidDeletions',
        'qc.overallScore',
        'coverage',
    ]

    for col in numeric_cols:
        if col in df.columns:
            features[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    print(f"Extracted {len(features.columns)} features: {list(features.columns)}")
    return features

def train_classifier(features, labels):
    """Train a Random Forest classifier on sequence features."""

    le = LabelEncoder()
    y = le.fit_transform(labels)
    X = features.values

    print(f"\nTraining on {len(X)} seqeunces")
    print(f"Classes: {le.classes_}")

    # Cross-validation
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    cv_scores = cross_val_score(clf, X, y, cv=min(2, len(X)), scoring='accuracy')
    print(f"\nCross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    # Train final model
    clf.fit(X, y)

    # Feature importance
    importance = pd.DataFrame({
        'feature': features.columns,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nTop features:\n{importance.head()}")

    return clf, le, importance

def main():
    parser = argparse.ArgumentParser(description='SARS-CoV-2 lineage classifier')
    parser.add_argument('--input', required=True, help='NextClade TSV file')
    parser.add_argument('--outdir', default='models', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Load data
    df = load_nextclade_output(args.input)

    # Extract features
    features = extract_features(df)

    # Use Nextclade pango lineage as label
    labels = df['Nextclade_pango'] if 'Nextclade_pango' in df.columns else df['clade']

    # Train
    clf, le, importance = train_classifier(features, labels)

    # Save feature importance
    importance.to_csv(f"{args.outdir}/feature_importance.csv", index=False)
    print(f"\nFeature importance saved to {args.outdir}/feature_importance.csv")
    print("\nDone. Model ready for prediction.")

if __name__ == '__main__':
    main()