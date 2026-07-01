# Public Dataset and Standards References

This folder records public references used for PlantMind AI demo dataset design.

## 1. AI4I 2020 Predictive Maintenance Dataset

AI4I is used as a public predictive maintenance reference.

### PlantMind Mapping

AI4I-style predictive maintenance behavior is mapped to:

- Asset: P-101 Pump
- Demo signal: vibration increase
- Failure context: bearing risk / machine failure risk
- PlantMind feature: maintenance intelligence and sensor-risk explanation

### Current Use

PlantMind AI already contains simplified synthetic sensor values in:

```text
data/raw/structured/sensor_readings.csv