# PlantMind Nexus Model Card

## Model Name

plantmind-p101-anomaly-detector

## Current Production Version

v0.3.11

## Task

Detect abnormal P-101 operating behavior from multivariate telemetry.

## Dataset Version

telemetry-demo-v1

## Feature Version

p101-multivariate-features-v1

## Metrics

| Metric | Value |
|---|---:|
| Precision | 0.94 |
| Recall | 0.91 |
| F1 score | 0.925 |
| ROC AUC | 0.96 |
| False positive rate | 0.04 |
| Model latency | 18 ms |

## Registry Stage

Production

## Approval

Approved by maintenance lead.

## Rollback Target

v0.3.10

## Intended Use

Industrial demo anomaly detection for P-101 maintenance intelligence.

## Limitations

This is a demo-grade model registry and telemetry dataset. Real deployment requires plant-specific calibration, validation, monitoring, and operator approval.
