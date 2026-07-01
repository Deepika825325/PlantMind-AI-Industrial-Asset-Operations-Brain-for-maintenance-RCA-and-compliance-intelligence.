# AI4I Mapping for PlantMind AI

## Purpose

This folder contains the AI4I 2020 Predictive Maintenance dataset used as a public reference for machine failure and predictive maintenance behavior.

PlantMind AI maps this dataset to the P-101 Pump demo use case.

## PlantMind Asset Mapping

| AI4I Concept | PlantMind AI Mapping |
|---|---|
| Machine condition | P-101 Pump condition |
| Machine failure | Pump failure risk |
| Rotational speed / torque / temperature | Pump operating condition signals |
| Failure label | Maintenance risk indicator |

## PlantMind Demo Use

The dataset supports this PlantMind AI story:

P-101 Pump is high risk because vibration increases above threshold, abnormal bearing noise is reported, and lubrication evidence is missing.

## Important Note

The PlantMind AI Day 2 demo already contains simplified sensor values in:

```text
data/raw/structured/sensor_readings.csv