# Public Dataset and Standards References

## Purpose

This folder records the external public references used for designing the PlantMind AI demo dataset.

PlantMind AI uses a hybrid dataset strategy:

1. Synthetic industrial documents created for the demo.
2. Public predictive-maintenance datasets used as reference or proxy data.
3. Public industrial standards context used for compliance-style checklist design.

The public references are used only to make the demo realistic and technically credible. The synthetic documents in this project are not real plant records.

---

## 1. DEXPI Reference

### Usage in PlantMind AI

DEXPI is used as a reference for creating a simplified P&ID-style drawing and drawing metadata.

PlantMind AI does not implement a full DEXPI parser in the MVP.

### Used For

* P&ID-style drawing concept
* Asset tag representation
* Equipment and instrument relationship metadata
* Drawing metadata structure

### Project File Created

```text
data/raw/documents/drawings/PID-001_Demo_Process_Line.png
data/raw/documents/drawings/PID-001_Demo_Process_Line.metadata.json
```

### PlantMind Mapping

```text
DEXPI-style P&ID reference
        ↓
Simplified demo drawing
        ↓
P-101 → C-201 → HX-301 process line
```

---

## 2. UCI AI4I 2020 Predictive Maintenance Dataset

### Usage in PlantMind AI

The UCI AI4I 2020 Predictive Maintenance dataset is used as a reference for predictive-maintenance-style machine failure data.

PlantMind AI uses it as inspiration for the synthetic sensor readings related to P-101 pump condition monitoring.

### Used For

* Predictive maintenance context
* Failure demo inspiration
* Sensor-style synthetic data
* Pump risk signal mapping

### Project File Created

```text
data/raw/structured/sensor_readings.csv
```

### PlantMind Mapping

```text
AI4I predictive maintenance machine condition
        ↓
P-101 pump vibration and bearing-risk demo
```

### Important Note

The `sensor_readings.csv` file is demo-mapped synthetic data. It is not a direct copy of the UCI AI4I dataset.

---

## 3. NASA C-MAPSS Reference

### Usage in PlantMind AI

NASA C-MAPSS is used as a reference for turbomachinery degradation and Remaining Useful Life behavior.

PlantMind AI uses it as inspiration for the C-201 compressor RUL trend.

### Used For

* Remaining Useful Life concept
* Degradation trend
* Compressor maintenance planning
* Sensor-risk explanation

### Project File Created

```text
data/raw/structured/sensor_readings.csv
```

### PlantMind Mapping

```text
NASA C-MAPSS turbomachinery degradation
        ↓
C-201 compressor decreasing RUL demo
```

### Important Note

The C-201 RUL values in `sensor_readings.csv` are simplified demo values inspired by RUL-style degradation behavior. They are not a full trained C-MAPSS model output.

---

## 4. OISD Standards Context

### Usage in PlantMind AI

OISD-style industrial safety and maintenance evidence context is used to design the compliance checklist.

PlantMind AI does not reproduce full OISD standards.

### Used For

* Work permit context
* Lockout tagout evidence context
* Maintenance evidence checklist
* Compliance gap design
* Safety-oriented maintenance workflow

### Project Files Created

```text
data/raw/documents/compliance/COMP-001_Compliance_Checklist.md
data/raw/documents/manuals_sops/SOP-GEN-001_Work_Permit_and_LOTO.md
data/raw/structured/ground_truth_compliance_gaps.csv
```

### PlantMind Mapping

```text
OISD-style compliance context
        ↓
Synthetic compliance checklist
        ↓
Missing, delayed, and overdue evidence gaps
```

---

## 5. Synthetic Data Transparency

PlantMind AI synthetic documents are created only for hackathon demonstration.

The following files are synthetic:

```text
SOP documents
Inspection reports
Incident reports
Compliance checklist
Work order CSV
Sensor readings CSV
Benchmark questions CSV
Ground-truth compliance gaps CSV
P&ID-style drawing metadata
```

Synthetic data is used because real industrial maintenance documents are usually confidential and not suitable for public hackathon use.

---

## 6. Final Dataset Mapping

| Reference Source                              | PlantMind Asset      | Project Usage                             |
| --------------------------------------------- | -------------------- | ----------------------------------------- |
| DEXPI-style P&ID reference                    | P-101, C-201, HX-301 | Demo process line drawing                 |
| UCI AI4I-style predictive maintenance context | P-101                | Pump vibration and bearing-risk demo      |
| NASA C-MAPSS-style degradation context        | C-201                | Compressor RUL trend demo                 |
| OISD-style compliance context                 | All assets           | Work permit, LOTO, and evidence checklist |

---

## 7. Responsible Use Statement

PlantMind AI is a decision-support demo.

It does not replace qualified engineers, plant operators, maintenance teams, or safety officers.

The system provides evidence-backed suggestions, but final maintenance and safety decisions must remain with qualified plant personnel.

---

## 8. Dataset Status

Current dataset phase:

```text
Day 2: Raw dataset collection and synthetic data creation
```

Day 2 expected outputs:

```text
data/raw/documents/
data/raw/structured/
data/raw/public_sources/
```
