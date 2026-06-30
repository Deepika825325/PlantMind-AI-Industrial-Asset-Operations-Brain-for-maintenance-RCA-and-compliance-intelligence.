# Dataset Plan

## Project Name

**PlantMind AI**

## Project Title

**PlantMind AI: Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence**

---

## 1. Purpose of This Document

This document defines the complete dataset strategy for PlantMind AI.

The goal is to make the project technically credible, demo-ready, and achievable within the hackathon timeline. PlantMind AI will not depend on one single dataset. Instead, it will use a hybrid dataset strategy:

1. **Public predictive-maintenance datasets** for sensor analytics, anomaly detection, and Remaining Useful Life demonstration.
2. **Synthetic industrial documents** for RAG, RCA, compliance checking, document intelligence, and knowledge graph generation.
3. **Preprocessed demo-ready data** for stable UI, reliable demo flow, and repeatable judge presentation.

This dataset plan is frozen for the project. No new asset category or unrelated dataset should be added after Day 1.

---

## 2. Dataset Strategy Summary

PlantMind AI is scoped to three assets only:

| Asset ID | Asset Name     | Asset Type         | Dataset Strategy                                                    |
| -------- | -------------- | ------------------ | ------------------------------------------------------------------- |
| P-101    | Pump           | Rotating Equipment | Bearing vibration dataset + synthetic maintenance documents         |
| C-201    | Compressor     | Rotating Equipment | RUL degradation dataset + synthetic maintenance documents           |
| HX-301   | Heat Exchanger | Process Equipment  | Process anomaly dataset + synthetic inspection/compliance documents |

The public datasets will provide technical credibility for predictive maintenance. The synthetic documents will provide realistic industrial context for document intelligence, RAG, RCA, and compliance workflows.

---

## 3. Final Dataset Sources

| Dataset                                         | Type                                   | Used For                         | Asset Mapping         | Project Purpose                                              |
| ----------------------------------------------- | -------------------------------------- | -------------------------------- | --------------------- | ------------------------------------------------------------ |
| NASA C-MAPSS                                    | Public time-series degradation dataset | Remaining Useful Life prediction | C-201 Compressor      | Show degradation trend and maintenance planning              |
| Case Western Reserve University Bearing Dataset | Public vibration/fault dataset         | Bearing fault classification     | P-101 Pump            | Show vibration-based rotating equipment fault intelligence   |
| Tennessee Eastman Process Dataset               | Public process simulation dataset      | Process anomaly detection        | HX-301 Heat Exchanger | Show process deviation and fouling-style anomaly explanation |
| Synthetic maintenance logs                      | Project-created document dataset       | RAG, maintenance history, RCA    | All assets            | Provide evidence for asset risk and recommendations          |
| Synthetic SOPs                                  | Project-created document dataset       | Safety procedure grounding       | All assets            | Provide procedural recommendations                           |
| Synthetic inspection reports                    | Project-created document dataset       | Compliance and evidence checking | All assets            | Support missing/available evidence detection                 |
| Synthetic incident reports                      | Project-created document dataset       | RCA generation                   | All assets            | Support failure investigation workflow                       |
| Synthetic compliance checklists                 | Project-created document dataset       | Compliance gap detection         | All assets            | Identify missing, delayed, and overdue evidence              |
| Synthetic drawings/images                       | Project-created visual dataset         | Asset tag extraction demo        | All assets            | Show document/image intelligence capability                  |

---

## 4. Why Public + Synthetic Dataset Combination Is Needed

PlantMind AI is not only a machine learning model. It is an industrial intelligence platform.

A public sensor dataset alone can show anomaly detection, but it cannot show:

* SOP-based reasoning
* Compliance evidence checking
* Root-cause analysis
* Asset-specific document retrieval
* Source citations
* Maintenance recommendations
* Knowledge graph relationships

A synthetic document dataset alone can show RAG, but it cannot show:

* Predictive maintenance
* Sensor trend analysis
* RUL estimation
* Vibration fault intelligence
* Process anomaly context

Therefore, the final dataset approach combines both.

The public datasets prove technical depth. The synthetic documents prove product usefulness and demo realism.

---

## 5. Public Dataset 1: NASA C-MAPSS

## 5.1 Dataset Name

**NASA C-MAPSS Jet Engine Simulated Data**

## 5.2 Project Mapping

| Field         | Value                                                 |
| ------------- | ----------------------------------------------------- |
| Mapped Asset  | C-201 Compressor                                      |
| Use Case      | Remaining Useful Life prediction                      |
| Demo Feature  | Compressor degradation trend and maintenance planning |
| Output Screen | Asset 360, Dashboard, Ask PlantMind                   |
| Priority      | High                                                  |

## 5.3 Dataset Description

NASA C-MAPSS consists of multiple multivariate time-series datasets. Each time series represents a different engine unit. The engine starts under normal operation and develops a fault over time. The training data runs until failure, while the test data ends before failure and includes true Remaining Useful Life values for evaluation. NASA describes the data as space-separated text files with 26 columns, including unit number, time in cycles, three operational settings, and sensor measurements.

## 5.4 Why This Dataset Is Used

This dataset is ideal for C-201 Compressor because compressors and turbomachinery assets commonly degrade over time. The dataset can be used to demonstrate:

* RUL prediction
* Degradation trend
* Maintenance planning
* Health score calculation
* Risk explanation

PlantMind AI will clearly state that C-MAPSS is used as a **turbomachinery degradation proxy** for the compressor demo. It is not claimed to be real compressor plant data.

## 5.5 Subset Selection

For the MVP and hackathon demo, use only:

```text
FD001
```

Reason:

* Single operating condition
* Single fault mode
* Easier preprocessing
* Faster model development
* More stable demo results

Optional extension after MVP:

```text
FD003
```

Reason:

* Includes two fault modes
* Better for advanced RUL explanation
* Useful only if time remains

## 5.6 Raw Files to Keep

Store the downloaded dataset under:

```text
data/raw/public/cmapss/
```

Expected files:

```text
train_FD001.txt
test_FD001.txt
RUL_FD001.txt
```

Optional files:

```text
train_FD003.txt
test_FD003.txt
RUL_FD003.txt
```

## 5.7 Columns

Use the following column naming convention:

```text
unit_id
cycle
op_setting_1
op_setting_2
op_setting_3
sensor_1
sensor_2
sensor_3
sensor_4
sensor_5
sensor_6
sensor_7
sensor_8
sensor_9
sensor_10
sensor_11
sensor_12
sensor_13
sensor_14
sensor_15
sensor_16
sensor_17
sensor_18
sensor_19
sensor_20
sensor_21
```

## 5.8 Preprocessing Steps

1. Load raw `.txt` files.
2. Assign column names.
3. Remove empty columns if present.
4. Sort by `unit_id` and `cycle`.
5. Calculate max cycle per unit.
6. Generate RUL label for training data:

```text
RUL = max_cycle_for_unit - current_cycle
```

7. Cap RUL if needed:

```text
RUL_CAPPED = min(RUL, 125)
```

8. Normalize sensor values.
9. Select important sensor features.
10. Create rolling statistics:

```text
rolling_mean_5
rolling_std_5
rolling_mean_10
rolling_std_10
```

11. Export processed file.

## 5.9 Processed Outputs

Store processed outputs under:

```text
data/processed/c201/
```

Files:

```text
c201_rul_train.csv
c201_rul_test.csv
c201_rul_predictions.csv
c201_sensor_trend.csv
c201_health_events.json
c201_rul_report.md
```

## 5.10 Model Plan

For hackathon delivery, use a simple but explainable baseline first.

### Baseline model

```text
Random Forest Regressor
```

or

```text
XGBoost Regressor
```

### Optional advanced model

```text
LSTM
```

The baseline is enough for the demo because PlantMind AI is judged as a full industrial intelligence platform, not only as a model benchmark.

## 5.11 Demo Output for C-201

Final demo statement:

```text
C-201 Compressor has a decreasing RUL trend. The system recommends inspection and filter replacement verification within the next maintenance window.
```

Expected UI values:

| Field                      | Value                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------ |
| Health Score               | 71%                                                                                  |
| Risk Level                 | Medium                                                                               |
| Main Signal                | Decreasing RUL                                                                       |
| Maintenance Recommendation | Inspect compressor and verify filter replacement                                     |
| Evidence Documents         | C-201_RUL_Report.pdf, C-201_Inspection_Report.pdf, C-201_Maintenance_Log_Feb2026.pdf |

---

## 6. Public Dataset 2: Case Western Reserve University Bearing Dataset

## 6.1 Dataset Name

**Case Western Reserve University Bearing Data Center Dataset**

## 6.2 Project Mapping

| Field         | Value                               |
| ------------- | ----------------------------------- |
| Mapped Asset  | P-101 Pump                          |
| Use Case      | Bearing vibration fault detection   |
| Demo Feature  | High-vibration fault intelligence   |
| Output Screen | Dashboard, Asset 360, RCA Workspace |
| Priority      | Very High                           |

## 6.3 Dataset Description

The Case Western Reserve University Bearing Data Center provides normal and faulty bearing data. The experiments used a 2 hp Reliance Electric motor, and acceleration data was measured near and remote from motor bearings. The bearing faults were seeded using electro-discharge machining at the inner raceway, rolling element, and outer raceway.

The data download page notes that normal bearings, drive-end defects, and fan-end defects are available, with data collected at 12,000 samples/second and 48,000 samples/second for drive-end bearing experiments. Files are provided in MATLAB format and contain fan-end vibration, drive-end vibration, base accelerometer data, and RPM data.

## 6.4 Why This Dataset Is Used

P-101 Pump is the main demo asset. The CWRU bearing dataset supports the story that P-101 has high vibration and possible bearing wear.

This dataset helps PlantMind AI show:

* Vibration-based condition monitoring
* Bearing fault classification
* Rotating equipment intelligence
* Maintenance recommendation generation
* RCA evidence support

PlantMind AI will clearly state that this dataset is used as a **bearing fault proxy** for the pump vibration demo.

## 6.5 Subset Selection

Use only the minimum subset needed for the demo:

```text
Normal baseline data
12k Drive End Bearing Fault Data
```

Fault classes to include:

```text
Normal
Inner Race Fault
Outer Race Fault
Ball Fault
```

This is enough for a strong demo.

## 6.6 Raw Files to Keep

Store raw data under:

```text
data/raw/public/cwru_bearing/
```

Suggested internal folders:

```text
normal/
inner_race_fault/
outer_race_fault/
ball_fault/
```

## 6.7 Preprocessing Steps

1. Load `.mat` files.
2. Extract vibration signal.
3. Use drive-end vibration signal first.
4. Segment signal into fixed-size windows.

Recommended window size:

```text
2048 samples
```

5. Generate labels:

```text
normal
inner_race_fault
outer_race_fault
ball_fault
```

6. Extract time-domain features:

```text
mean
standard_deviation
rms
kurtosis
skewness
peak_to_peak
crest_factor
```

7. Extract frequency-domain features:

```text
dominant_frequency
spectral_energy
band_power
fft_peak
```

8. Train simple classifier.
9. Export predictions and feature summary.

## 6.8 Processed Outputs

Store processed files under:

```text
data/processed/p101/
```

Files:

```text
p101_vibration_features.csv
p101_fault_predictions.csv
p101_vibration_trend.csv
p101_fault_summary.json
p101_bearing_fault_report.md
```

## 6.9 Model Plan

### Baseline model

```text
Random Forest Classifier
```

or

```text
Support Vector Machine
```

### Optional advanced model

```text
1D CNN
```

For hackathon delivery, a Random Forest classifier with feature extraction is enough. It is explainable, fast, and stable.

## 6.10 Demo Output for P-101

Final demo statement:

```text
P-101 shows a vibration pattern consistent with bearing fault behavior. Combined with missing lubrication evidence and maintenance log symptoms, PlantMind marks P-101 as high risk.
```

Expected UI values:

| Field                      | Value                                                                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------------- |
| Health Score               | 62%                                                                                                   |
| Risk Level                 | High                                                                                                  |
| Main Signal                | High vibration                                                                                        |
| Possible Failure Mode      | Bearing wear                                                                                          |
| Maintenance Recommendation | Inspect bearing housing, verify lubrication, check alignment                                          |
| Evidence Documents         | P-101_Inspection_Report_IR-008.pdf, P-101_Maintenance_Log_Jan2026.pdf, P-101_Compliance_Checklist.pdf |

---

## 7. Public Dataset 3: Tennessee Eastman Process Dataset

## 7.1 Dataset Name

**Tennessee Eastman Process Dataset**

## 7.2 Project Mapping

| Field         | Value                                   |
| ------------- | --------------------------------------- |
| Mapped Asset  | HX-301 Heat Exchanger                   |
| Use Case      | Process anomaly detection               |
| Demo Feature  | Fouling-style process deviation         |
| Output Screen | Dashboard, Asset 360, Compliance Center |
| Priority      | Medium                                  |

## 7.3 Dataset Description

The Tennessee Eastman Process dataset is a process simulation dataset used for process control and fault detection research in chemical engineering. The referenced open dataset contains simulation data for multiple operating modes and 21 standard fault scenarios. It includes process variables such as temperatures, pressures, flow rates, manipulated variables, measured disturbances, and fault indicators.

## 7.4 Why This Dataset Is Used

HX-301 is a heat exchanger. Direct public heat exchanger fouling datasets are harder to use quickly in a hackathon setting. The Tennessee Eastman Process dataset gives realistic process time-series behavior that can be mapped to a heat-transfer deviation use case.

PlantMind AI will clearly state that this is used as a **process anomaly proxy** for HX-301 and not as a direct physical fouling dataset.

## 7.5 Subset Selection

Use only one operating mode and one or two fault files.

Recommended:

```text
Mode 1 normal operation
Mode 1 fault scenario related to temperature/cooling disturbance
```

Possible fault scenarios to map:

```text
Condenser cooling water inlet temperature
Condenser cooling water valve
Reactor cooling water inlet temperature
Reactor cooling water valve
```

For PlantMind AI, convert selected process anomaly into the business-language issue:

```text
HX-301 shows reduced heat transfer efficiency and possible fouling.
```

## 7.6 Raw Files to Keep

Store raw data under:

```text
data/raw/public/tennessee_eastman/
```

Suggested files:

```text
mode1_normal_50.xlsx
mode1_fault_temperature_or_cooling.xlsx
```

## 7.7 Preprocessing Steps

1. Load normal operation file.
2. Load selected fault operation file.
3. Select relevant process variables:

```text
temperature
pressure
flow
cooling-related variables
valve-related variables
```

4. Create derived heat exchanger-style features:

```text
temperature_delta
pressure_drop
efficiency_index
normalized_flow
```

5. Generate anomaly labels:

```text
normal
warning
anomaly
```

6. Export a demo-ready HX-301 trend.

## 7.8 Processed Outputs

Store processed files under:

```text
data/processed/hx301/
```

Files:

```text
hx301_process_trend.csv
hx301_anomaly_events.csv
hx301_efficiency_index.csv
hx301_fouling_summary.json
hx301_process_anomaly_report.md
```

## 7.9 Model Plan

### Baseline approach

Use rule-based anomaly detection first:

```text
If pressure_drop increases and temperature_delta decreases, mark fouling suspected.
```

### Optional ML approach

```text
Isolation Forest
```

or

```text
One-Class SVM
```

For hackathon delivery, rule-based anomaly detection is acceptable because the main value of HX-301 is compliance and process explanation.

## 7.10 Demo Output for HX-301

Final demo statement:

```text
HX-301 shows reduced heat transfer efficiency, increasing pressure drop, and overdue cleaning evidence. PlantMind marks fouling as suspected and recommends cleaning inspection.
```

Expected UI values:

| Field                      | Value                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| Health Score               | 68%                                                                                       |
| Risk Level                 | Medium                                                                                    |
| Main Signal                | Reduced efficiency                                                                        |
| Possible Failure Mode      | Fouling                                                                                   |
| Maintenance Recommendation | Schedule cleaning inspection                                                              |
| Evidence Documents         | HX-301_Inspection_Report.pdf, HX-301_Cleaning_Record.pdf, HX-301_Compliance_Checklist.pdf |

---

## 8. Synthetic Industrial Document Dataset

## 8.1 Purpose

The synthetic document dataset is the most important dataset for the RAG, RCA, compliance, and knowledge graph parts of PlantMind AI.

The documents should look realistic but should be clearly marked as synthetic demo data.

## 8.2 Why Synthetic Documents Are Acceptable

The hackathon problem focuses on industrial knowledge intelligence. Real industrial maintenance documents are usually confidential, proprietary, or unavailable publicly. Therefore, synthetic documents are acceptable as long as they are:

* Realistic
* Consistent
* Asset-specific
* Structured enough for extraction
* Clearly labeled as synthetic
* Designed to support the demo workflow

## 8.3 Synthetic Document Rules

All synthetic documents must follow these rules:

1. Every document must mention one of the frozen asset IDs:

```text
P-101
C-201
HX-301
```

2. Every document must have a document ID.
3. Every document must have a document type.
4. Every document must have a date.
5. Every document must have asset-specific evidence.
6. Every important claim must be consistent across files.
7. Contradictions should be avoided unless intentionally used for demo.
8. Every document should be short enough for fast indexing.
9. Every document should support citations in the RAG answer.
10. Every document should be stored in the correct asset folder.

---

## 9. Synthetic Documents for P-101 Pump

## 9.1 P-101 Document List

Store under:

```text
data/raw/documents/P-101/
```

Files:

```text
P-101_Datasheet.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Inspection_Report_IR-008.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Incident_Report_High_Vibration.pdf
P-101_Compliance_Checklist.pdf
P-101_Pump_Drawing.png
```

## 9.2 Required Facts for P-101

All P-101 documents must consistently support this story:

```text
P-101 is high risk because it has high vibration, abnormal bearing noise, slightly elevated bearing temperature, and missing lubrication evidence.
```

## 9.3 Document-Level Content Plan

### 9.3.1 P-101_Datasheet.pdf

Required content:

```text
Asset ID: P-101
Asset Name: Cooling Water Circulation Pump
Asset Type: Centrifugal Pump
Criticality: High
Location: Utility Area - Line A
Normal Vibration Threshold: 4.5 mm/s
Warning Vibration Threshold: 6.0 mm/s
Critical Vibration Threshold: 7.5 mm/s
Normal Bearing Temperature: 65°C
Maximum Bearing Temperature: 80°C
Maintenance Frequency: Weekly lubrication inspection
```

### 9.3.2 P-101_Maintenance_Log_Jan2026.pdf

Required content:

```text
Document ID: ML-014
Asset ID: P-101
Date: 2026-01-18
Technician: Demo Technician
Observation: Abnormal bearing noise observed during routine operation.
Observation: Lubrication condition could not be verified because evidence record was missing.
Action Taken: Pump kept under observation.
Recommended Action: Inspect bearing housing and verify lubrication level.
```

### 9.3.3 P-101_Inspection_Report_IR-008.pdf

Required content:

```text
Document ID: IR-008
Asset ID: P-101
Date: 2026-01-21
Inspection Type: Vibration Inspection
Measured Vibration: 7.8 mm/s
Threshold: 6.0 mm/s warning, 7.5 mm/s critical
Finding: Vibration exceeded critical threshold.
Finding: Slightly elevated bearing temperature recorded at 78°C.
Recommendation: Check bearing condition, shaft alignment, and lubrication.
```

### 9.3.4 P-101_SOP_Lubrication_and_Bearing_Check.pdf

Required content:

```text
Document ID: SOP-PUMP-01
Asset ID: P-101
Procedure: Lubrication and Bearing Check
Frequency: Weekly
Requirement: Verify lubrication level and lubricant condition.
Requirement: Record lubrication evidence after every inspection.
Safety Note: Lockout/tagout procedure must be followed before physical inspection.
Escalation: If vibration exceeds 7.5 mm/s, schedule immediate bearing inspection.
```

### 9.3.5 P-101_Incident_Report_High_Vibration.pdf

Required content:

```text
Document ID: INC-P101-026
Asset ID: P-101
Incident Type: High Vibration Event
Date: 2026-01-22
Symptom: Repeated high vibration during normal load.
Suspected Cause: Bearing wear, lubrication degradation, or misalignment.
Temporary Action: Operator reduced load and informed maintenance team.
Required Follow-Up: RCA and bearing inspection.
```

### 9.3.6 P-101_Compliance_Checklist.pdf

Required content:

```text
Document ID: CC-P101-001
Asset ID: P-101
Compliance Requirement: Weekly vibration inspection
Status: Available
Evidence: P-101_Inspection_Report_IR-008.pdf

Compliance Requirement: Weekly lubrication check
Status: Missing
Evidence: Not available

Compliance Gap: Lubrication evidence missing for current week.
```

### 9.3.7 P-101_Pump_Drawing.png

Required content:

The image should be a simple diagram with the following labels:

```text
P-101
Pump
Motor
Bearing Housing
Discharge Line
Suction Line
Vibration Sensor
```

The drawing does not need to be a real engineering drawing. It only needs to support asset tag extraction and visual document intelligence demo.

---

## 10. Synthetic Documents for C-201 Compressor

## 10.1 C-201 Document List

Store under:

```text
data/raw/documents/C-201/
```

Files:

```text
C-201_Datasheet.pdf
C-201_Maintenance_Log_Feb2026.pdf
C-201_RUL_Report.pdf
C-201_SOP_Compressor_Shutdown.pdf
C-201_Inspection_Report.pdf
C-201_Compliance_Checklist.pdf
C-201_Compressor_Drawing.png
```

## 10.2 Required Facts for C-201

All C-201 documents must consistently support this story:

```text
C-201 has a decreasing RUL trend, unstable pressure ratio, increasing outlet temperature, and delayed filter replacement verification.
```

## 10.3 Document-Level Content Plan

### 10.3.1 C-201_Datasheet.pdf

Required content:

```text
Asset ID: C-201
Asset Name: Process Air Compressor
Asset Type: Compressor
Criticality: Medium-High
Location: Compression Area - Train B
Normal Outlet Temperature Range: 70°C to 85°C
Warning Outlet Temperature: 90°C
Normal Pressure Ratio Range: 3.2 to 3.8
Maintenance Frequency: Monthly inspection
```

### 10.3.2 C-201_Maintenance_Log_Feb2026.pdf

Required content:

```text
Document ID: ML-C201-022
Asset ID: C-201
Date: 2026-02-10
Observation: Filter replacement was planned but completion evidence is delayed.
Observation: Outlet temperature trend is increasing.
Observation: Pressure ratio instability was observed during operation.
Recommended Action: Verify filter replacement and inspect compressor during next maintenance window.
```

### 10.3.3 C-201_RUL_Report.pdf

Required content:

```text
Document ID: RUL-C201-001
Asset ID: C-201
Model Source: C-MAPSS-based RUL baseline
Estimated RUL Trend: Decreasing
Risk Level: Medium
Recommendation: Schedule inspection within next maintenance window.
Note: This RUL estimate is generated from a public turbomachinery degradation dataset mapped to compressor demo behavior.
```

### 10.3.4 C-201_SOP_Compressor_Shutdown.pdf

Required content:

```text
Document ID: SOP-COMP-01
Asset ID: C-201
Procedure: Compressor Safe Shutdown
Requirement: Notify operations before shutdown.
Requirement: Depressurize system before maintenance.
Requirement: Verify temperature and pressure stabilization before inspection.
Requirement: Use lockout/tagout procedure.
```

### 10.3.5 C-201_Inspection_Report.pdf

Required content:

```text
Document ID: IR-C201-011
Asset ID: C-201
Date: 2026-02-15
Inspection Type: Monthly Compressor Inspection
Finding: Outlet temperature increased compared to previous inspection.
Finding: Pressure ratio showed instability during loaded operation.
Recommendation: Verify filter replacement, inspect compressor stage, and monitor RUL trend.
```

### 10.3.6 C-201_Compliance_Checklist.pdf

Required content:

```text
Document ID: CC-C201-001
Asset ID: C-201
Compliance Requirement: Monthly compressor inspection
Status: Available
Evidence: C-201_Inspection_Report.pdf

Compliance Requirement: Filter replacement verification
Status: Delayed
Evidence: Maintenance log indicates pending verification.
```

### 10.3.7 C-201_Compressor_Drawing.png

Required content:

The image should contain:

```text
C-201
Compressor
Inlet Filter
Compressor Stage
Outlet Line
Temperature Sensor
Pressure Sensor
```

---

## 11. Synthetic Documents for HX-301 Heat Exchanger

## 11.1 HX-301 Document List

Store under:

```text
data/raw/documents/HX-301/
```

Files:

```text
HX-301_Datasheet.pdf
HX-301_Inspection_Report.pdf
HX-301_Cleaning_Record.pdf
HX-301_SOP_Pressure_Test.pdf
HX-301_Compliance_Checklist.pdf
HX-301_Incident_Report_Low_Efficiency.pdf
HX-301_Heat_Exchanger_Drawing.png
```

## 11.2 Required Facts for HX-301

All HX-301 documents must consistently support this story:

```text
HX-301 has suspected fouling because outlet temperature is below target, pressure drop is increasing, and cleaning evidence is overdue or missing.
```

## 11.3 Document-Level Content Plan

### 11.3.1 HX-301_Datasheet.pdf

Required content:

```text
Asset ID: HX-301
Asset Name: Feed Preheater Heat Exchanger
Asset Type: Shell and Tube Heat Exchanger
Criticality: Medium
Location: Process Area - Unit C
Target Outlet Temperature: 95°C
Minimum Acceptable Outlet Temperature: 90°C
Normal Pressure Drop: 1.2 bar
Warning Pressure Drop: 1.8 bar
Maintenance Frequency: Cleaning inspection every 30 days
```

### 11.3.2 HX-301_Inspection_Report.pdf

Required content:

```text
Document ID: IR-HX301-009
Asset ID: HX-301
Date: 2026-03-05
Inspection Type: Performance Inspection
Finding: Outlet temperature recorded at 88°C, below acceptable target.
Finding: Pressure drop increased to 1.9 bar.
Possible Cause: Fouling or restricted flow.
Recommendation: Schedule cleaning inspection and verify tube-side condition.
```

### 11.3.3 HX-301_Cleaning_Record.pdf

Required content:

```text
Document ID: CR-HX301-002
Asset ID: HX-301
Last Cleaning Date: 2026-01-28
Required Frequency: Every 30 days
Current Status: Cleaning evidence overdue
Finding: No current cleaning confirmation found for latest inspection cycle.
```

### 11.3.4 HX-301_SOP_Pressure_Test.pdf

Required content:

```text
Document ID: SOP-HX-01
Asset ID: HX-301
Procedure: Heat Exchanger Pressure Test
Requirement: Isolate exchanger before pressure test.
Requirement: Confirm pressure test report after maintenance.
Requirement: Inspect for leakage before return to service.
Requirement: Record evidence after test completion.
```

### 11.3.5 HX-301_Compliance_Checklist.pdf

Required content:

```text
Document ID: CC-HX301-001
Asset ID: HX-301
Compliance Requirement: Pressure test report
Status: Available
Evidence: SOP-HX-01 and pressure test record available

Compliance Requirement: Cleaning and fouling inspection
Status: Overdue
Evidence: Current cleaning record missing

Compliance Gap: Cleaning evidence overdue for HX-301.
```

### 11.3.6 HX-301_Incident_Report_Low_Efficiency.pdf

Required content:

```text
Document ID: INC-HX301-017
Asset ID: HX-301
Incident Type: Low Heat Transfer Efficiency
Date: 2026-03-07
Symptom: Outlet temperature below target.
Symptom: Pressure drop increased.
Suspected Cause: Fouling or tube-side restriction.
Recommended Action: Schedule cleaning inspection and review operating conditions.
```

### 11.3.7 HX-301_Heat_Exchanger_Drawing.png

Required content:

The image should contain:

```text
HX-301
Shell Side
Tube Side
Hot Inlet
Hot Outlet
Cold Inlet
Cold Outlet
Temperature Sensor
Pressure Indicator
```

---

## 12. Synthetic Dataset Metadata Schema

Every document should have metadata extracted into a structured JSON format.

## 12.1 Document Metadata Schema

```json
{
  "document_id": "IR-008",
  "file_name": "P-101_Inspection_Report_IR-008.pdf",
  "asset_id": "P-101",
  "asset_name": "Cooling Water Circulation Pump",
  "document_type": "Inspection Report",
  "document_date": "2026-01-21",
  "source_type": "synthetic",
  "indexed": true,
  "tags": ["high vibration", "bearing noise", "bearing temperature"],
  "summary": "Inspection report showing P-101 vibration above critical threshold.",
  "compliance_relevant": true
}
```

## 12.2 Asset Metadata Schema

```json
{
  "asset_id": "P-101",
  "asset_name": "Cooling Water Circulation Pump",
  "asset_type": "Pump",
  "criticality": "High",
  "location": "Utility Area - Line A",
  "health_score": 62,
  "risk_level": "High",
  "main_issue": "High vibration",
  "possible_failure_mode": "Bearing wear",
  "recommended_action": "Inspect bearing housing and verify lubrication"
}
```

## 12.3 Compliance Metadata Schema

```json
{
  "asset_id": "P-101",
  "requirement": "Weekly lubrication check",
  "expected_evidence": "Lubrication record",
  "status": "Missing",
  "evidence_file": null,
  "gap_reason": "No lubrication evidence found for current week",
  "recommended_action": "Upload lubrication record or perform lubrication inspection"
}
```

## 12.4 Knowledge Graph Triple Schema

```json
{
  "source": "P-101",
  "relationship": "HAS_SYMPTOM",
  "target": "High Vibration",
  "evidence_document": "P-101_Inspection_Report_IR-008.pdf"
}
```

---

## 13. Final Processed Dataset Structure

The project should generate processed files that are easy for the frontend and backend to consume.

Store processed demo data under:

```text
data/demo/
```

Required files:

```text
assets.json
documents.json
compliance_matrix.json
maintenance_events.json
health_scores.json
knowledge_graph.json
rag_seed_questions.json
demo_answers.json
```

## 13.1 assets.json

Purpose:

Used by Dashboard and Asset 360.

Example:

```json
[
  {
    "asset_id": "P-101",
    "asset_name": "Cooling Water Circulation Pump",
    "asset_type": "Pump",
    "health_score": 62,
    "risk_level": "High",
    "main_issue": "High vibration + missing lubrication evidence"
  },
  {
    "asset_id": "C-201",
    "asset_name": "Process Air Compressor",
    "asset_type": "Compressor",
    "health_score": 71,
    "risk_level": "Medium",
    "main_issue": "RUL decreasing + delayed filter replacement"
  },
  {
    "asset_id": "HX-301",
    "asset_name": "Feed Preheater Heat Exchanger",
    "asset_type": "Heat Exchanger",
    "health_score": 68,
    "risk_level": "Medium",
    "main_issue": "Fouling suspected + cleaning overdue"
  }
]
```

## 13.2 documents.json

Purpose:

Used by Document Library and RAG source citation panel.

Required fields:

```json
{
  "document_id": "IR-008",
  "file_name": "P-101_Inspection_Report_IR-008.pdf",
  "asset_id": "P-101",
  "document_type": "Inspection Report",
  "document_date": "2026-01-21",
  "indexed": true,
  "tags": ["vibration", "bearing", "inspection"],
  "summary": "P-101 vibration exceeded critical threshold."
}
```

## 13.3 compliance_matrix.json

Purpose:

Used by Compliance Center.

Required fields:

```json
{
  "asset_id": "P-101",
  "requirement": "Weekly lubrication check",
  "expected_evidence": "Lubrication record",
  "status": "Missing",
  "evidence_file": null,
  "recommended_action": "Perform lubrication check and upload evidence"
}
```

## 13.4 maintenance_events.json

Purpose:

Used by Asset 360 maintenance timeline.

Required fields:

```json
{
  "asset_id": "P-101",
  "event_id": "ML-014",
  "event_date": "2026-01-18",
  "event_type": "Maintenance Observation",
  "description": "Abnormal bearing noise observed.",
  "recommended_action": "Inspect bearing housing and verify lubrication"
}
```

## 13.5 health_scores.json

Purpose:

Used by Dashboard and Asset 360.

Required fields:

```json
{
  "asset_id": "P-101",
  "health_score": 62,
  "risk_level": "High",
  "risk_drivers": [
    "Vibration above threshold",
    "Abnormal bearing noise",
    "Missing lubrication evidence"
  ]
}
```

## 13.6 knowledge_graph.json

Purpose:

Used by Knowledge Graph screen.

Required node format:

```json
{
  "id": "P-101",
  "label": "P-101 Pump",
  "type": "asset"
}
```

Required edge format:

```json
{
  "source": "P-101",
  "target": "High Vibration",
  "relationship": "HAS_SYMPTOM",
  "evidence": "P-101_Inspection_Report_IR-008.pdf"
}
```

## 13.7 rag_seed_questions.json

Purpose:

Used by Ask PlantMind suggested question chips.

Required questions:

```json
[
  {
    "question": "Why is P-101 high risk?",
    "asset_id": "P-101",
    "category": "risk_explanation"
  },
  {
    "question": "Generate RCA for P-101 high vibration.",
    "asset_id": "P-101",
    "category": "rca"
  },
  {
    "question": "Which assets are non-compliant?",
    "asset_id": "ALL",
    "category": "compliance"
  },
  {
    "question": "What maintenance should be planned for C-201?",
    "asset_id": "C-201",
    "category": "maintenance_planning"
  },
  {
    "question": "What evidence is missing for HX-301?",
    "asset_id": "HX-301",
    "category": "compliance"
  }
]
```

---

## 14. Folder Structure

Use this final dataset folder structure.

```text
data/
├── raw/
│   ├── public/
│   │   ├── cmapss/
│   │   │   ├── train_FD001.txt
│   │   │   ├── test_FD001.txt
│   │   │   └── RUL_FD001.txt
│   │   │
│   │   ├── cwru_bearing/
│   │   │   ├── normal/
│   │   │   ├── inner_race_fault/
│   │   │   ├── outer_race_fault/
│   │   │   └── ball_fault/
│   │   │
│   │   └── tennessee_eastman/
│   │       ├── mode1_normal_50.xlsx
│   │       └── mode1_fault_temperature_or_cooling.xlsx
│   │
│   └── documents/
│       ├── P-101/
│       │   ├── P-101_Datasheet.pdf
│       │   ├── P-101_Maintenance_Log_Jan2026.pdf
│       │   ├── P-101_Inspection_Report_IR-008.pdf
│       │   ├── P-101_SOP_Lubrication_and_Bearing_Check.pdf
│       │   ├── P-101_Incident_Report_High_Vibration.pdf
│       │   ├── P-101_Compliance_Checklist.pdf
│       │   └── P-101_Pump_Drawing.png
│       │
│       ├── C-201/
│       │   ├── C-201_Datasheet.pdf
│       │   ├── C-201_Maintenance_Log_Feb2026.pdf
│       │   ├── C-201_RUL_Report.pdf
│       │   ├── C-201_SOP_Compressor_Shutdown.pdf
│       │   ├── C-201_Inspection_Report.pdf
│       │   ├── C-201_Compliance_Checklist.pdf
│       │   └── C-201_Compressor_Drawing.png
│       │
│       └── HX-301/
│           ├── HX-301_Datasheet.pdf
│           ├── HX-301_Inspection_Report.pdf
│           ├── HX-301_Cleaning_Record.pdf
│           ├── HX-301_SOP_Pressure_Test.pdf
│           ├── HX-301_Compliance_Checklist.pdf
│           ├── HX-301_Incident_Report_Low_Efficiency.pdf
│           └── HX-301_Heat_Exchanger_Drawing.png
│
├── processed/
│   ├── p101/
│   │   ├── p101_vibration_features.csv
│   │   ├── p101_fault_predictions.csv
│   │   ├── p101_vibration_trend.csv
│   │   └── p101_fault_summary.json
│   │
│   ├── c201/
│   │   ├── c201_rul_train.csv
│   │   ├── c201_rul_test.csv
│   │   ├── c201_rul_predictions.csv
│   │   └── c201_sensor_trend.csv
│   │
│   └── hx301/
│       ├── hx301_process_trend.csv
│       ├── hx301_anomaly_events.csv
│       ├── hx301_efficiency_index.csv
│       └── hx301_fouling_summary.json
│
└── demo/
    ├── assets.json
    ├── documents.json
    ├── compliance_matrix.json
    ├── maintenance_events.json
    ├── health_scores.json
    ├── knowledge_graph.json
    ├── rag_seed_questions.json
    └── demo_answers.json
```

---

## 15. Document Ingestion Plan

## 15.1 Input

The ingestion pipeline should read documents from:

```text
data/raw/documents/
```

## 15.2 Supported File Types

For the hackathon demo, support only:

```text
.pdf
.txt
.md
.png
.jpg
.jpeg
```

## 15.3 Ingestion Steps

1. Read file.
2. Extract text.
3. Detect asset ID.
4. Detect document type.
5. Extract metadata.
6. Chunk document.
7. Add metadata to each chunk.
8. Generate embeddings.
9. Store chunks in vector database.
10. Store metadata in PostgreSQL.
11. Generate graph entities and relationships.

## 15.4 Chunking Strategy

Use small chunks for better citation quality.

Recommended:

```text
chunk_size = 500 tokens
chunk_overlap = 80 tokens
```

Every chunk must include metadata:

```json
{
  "asset_id": "P-101",
  "document_id": "IR-008",
  "file_name": "P-101_Inspection_Report_IR-008.pdf",
  "document_type": "Inspection Report",
  "chunk_index": 3
}
```

## 15.5 Embedding Storage

Store embeddings in:

```text
PostgreSQL + pgvector
```

Recommended vector table:

```text
document_chunks
```

Fields:

```text
id
asset_id
document_id
file_name
document_type
chunk_text
embedding
created_at
```

---

## 16. Knowledge Graph Dataset Plan

## 16.1 Graph Source

The graph should be generated from synthetic documents and processed metadata.

## 16.2 Node Types

Only these node types are in scope:

```text
Asset
Document
Symptom
Failure Mode
Maintenance Action
Compliance Requirement
```

## 16.3 Relationship Types

Only these relationship types are in scope:

```text
HAS_DOCUMENT
HAS_SYMPTOM
INDICATES_FAILURE
REQUIRES_ACTION
HAS_COMPLIANCE_REQUIREMENT
EVIDENCE_FOR
```

## 16.4 Required Graph Paths

### P-101

```text
P-101 → High Vibration → Bearing Wear → Inspect Bearing Housing
P-101 → Lubrication Evidence Missing → Weekly Lubrication Check
P-101 → P-101_Inspection_Report_IR-008.pdf → High Vibration
```

### C-201

```text
C-201 → Decreasing RUL → Compressor Inspection
C-201 → Delayed Filter Replacement → Verify Filter Replacement
C-201 → C-201_RUL_Report.pdf → Maintenance Planning
```

### HX-301

```text
HX-301 → Reduced Outlet Temperature → Fouling Suspected
HX-301 → Cleaning Evidence Overdue → Cleaning Inspection
HX-301 → HX-301_Inspection_Report.pdf → Pressure Drop Increased
```

---

## 17. Compliance Dataset Plan

## 17.1 Compliance Matrix

The compliance dataset must contain these final rows.

| Asset  | Requirement                     | Evidence                           | Status    | Recommended Action                          |
| ------ | ------------------------------- | ---------------------------------- | --------- | ------------------------------------------- |
| P-101  | Weekly vibration inspection     | P-101_Inspection_Report_IR-008.pdf | Available | Continue vibration monitoring               |
| P-101  | Weekly lubrication check        | Missing                            | Missing   | Perform lubrication check and upload record |
| C-201  | Monthly compressor inspection   | C-201_Inspection_Report.pdf        | Available | Continue monthly inspection cycle           |
| C-201  | Filter replacement verification | C-201_Maintenance_Log_Feb2026.pdf  | Delayed   | Verify filter replacement completion        |
| HX-301 | Pressure test report            | HX-301_SOP_Pressure_Test.pdf       | Available | Keep pressure evidence updated              |
| HX-301 | Cleaning and fouling inspection | Missing or overdue                 | Overdue   | Schedule cleaning inspection                |

## 17.2 Status Values

Only these status values are allowed:

```text
Available
Missing
Overdue
Delayed
Not Required
```

## 17.3 Compliance Summary Expected Output

```text
PlantMind found compliance gaps for two assets.

P-101 has missing weekly lubrication evidence.
HX-301 has overdue cleaning and fouling inspection evidence.
C-201 has available monthly inspection evidence, but filter replacement verification is delayed.

Recommended next steps:
1. Upload or complete P-101 lubrication record.
2. Schedule HX-301 cleaning inspection.
3. Verify C-201 filter replacement completion.
```

---

## 18. Demo Answer Dataset

To keep the demo stable, create a `demo_answers.json` file with high-confidence expected answers.

This does not mean the system is fake. It means the demo has known validation questions and expected answer style.

## 18.1 Required Demo Questions

```json
[
  {
    "question": "Why is P-101 high risk?",
    "expected_sources": [
      "P-101_Inspection_Report_IR-008.pdf",
      "P-101_Maintenance_Log_Jan2026.pdf",
      "P-101_SOP_Lubrication_and_Bearing_Check.pdf",
      "P-101_Compliance_Checklist.pdf"
    ]
  },
  {
    "question": "Generate RCA for P-101 high vibration.",
    "expected_sources": [
      "P-101_Inspection_Report_IR-008.pdf",
      "P-101_Maintenance_Log_Jan2026.pdf",
      "P-101_Compliance_Checklist.pdf"
    ]
  },
  {
    "question": "Which assets are non-compliant?",
    "expected_sources": [
      "P-101_Compliance_Checklist.pdf",
      "HX-301_Compliance_Checklist.pdf",
      "C-201_Compliance_Checklist.pdf"
    ]
  },
  {
    "question": "What maintenance should be planned for C-201?",
    "expected_sources": [
      "C-201_RUL_Report.pdf",
      "C-201_Inspection_Report.pdf",
      "C-201_Maintenance_Log_Feb2026.pdf"
    ]
  },
  {
    "question": "What evidence is missing for HX-301?",
    "expected_sources": [
      "HX-301_Inspection_Report.pdf",
      "HX-301_Cleaning_Record.pdf",
      "HX-301_Compliance_Checklist.pdf"
    ]
  }
]
```

---

## 19. Data Validation Rules

Before demo, validate the dataset using these checks.

## 19.1 Asset ID Validation

Every document must contain one valid asset ID:

```text
P-101
C-201
HX-301
```

## 19.2 Document Type Validation

Every document must map to one of these document types:

```text
Datasheet
Maintenance Log
Inspection Report
SOP
Incident Report
Compliance Checklist
Drawing
RUL Report
Cleaning Record
```

## 19.3 Citation Validation

Every expected RAG answer must cite at least two documents.

For P-101 high-risk answer, required sources are:

```text
P-101_Inspection_Report_IR-008.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Compliance_Checklist.pdf
```

## 19.4 Compliance Validation

Compliance status must match the frozen project story.

Final expected statuses:

```text
P-101 lubrication evidence: Missing
C-201 filter replacement verification: Delayed
HX-301 cleaning evidence: Overdue
```

## 19.5 Health Score Validation

Final health scores must remain fixed for demo consistency:

```text
P-101: 62
C-201: 71
HX-301: 68
```

---

## 20. Health Score Dataset Rules

The health score will be calculated using rule-based logic for the hackathon.

## 20.1 Scoring Formula

```text
Base health score = 100

Subtract:
- 20 points for critical sensor anomaly
- 15 points for missing compliance evidence
- 10 points for overdue maintenance
- 10 points for repeated maintenance symptom
- 5 points for delayed evidence
```

## 20.2 Final Demo Scores

| Asset  | Base | Deductions                                                           | Final Score |
| ------ | ---: | -------------------------------------------------------------------- | ----------: |
| P-101  |  100 | Critical vibration, missing lubrication, bearing noise               |          62 |
| C-201  |  100 | Decreasing RUL, delayed filter verification, temperature trend       |          71 |
| HX-301 |  100 | Fouling suspected, overdue cleaning evidence, pressure drop increase |          68 |

## 20.3 Risk Level Rules

```text
Health Score >= 80: Low Risk
Health Score 65-79: Medium Risk
Health Score < 65: High Risk
```

Final risk levels:

```text
P-101: High
C-201: Medium
HX-301: Medium
```

---

## 21. Dataset Creation Timeline

## Day 1

Create this dataset plan and freeze dataset scope.

Deliverables:

```text
docs/dataset_plan.md
data/raw/documents/P-101/
data/raw/documents/C-201/
data/raw/documents/HX-301/
```

## Day 2

Create synthetic documents for P-101.

Deliverables:

```text
P-101_Datasheet.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Inspection_Report_IR-008.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Incident_Report_High_Vibration.pdf
P-101_Compliance_Checklist.pdf
```

## Day 3

Create synthetic documents for C-201 and HX-301.

Deliverables:

```text
C-201 document pack
HX-301 document pack
```

## Day 4

Download and preprocess public datasets.

Deliverables:

```text
c201_rul_predictions.csv
p101_fault_predictions.csv
hx301_process_trend.csv
```

## Day 5

Create demo-ready JSON files.

Deliverables:

```text
assets.json
documents.json
compliance_matrix.json
maintenance_events.json
health_scores.json
knowledge_graph.json
rag_seed_questions.json
demo_answers.json
```

---

## 22. Minimum Viable Dataset

If time becomes limited, the minimum dataset required for a successful demo is:

## 22.1 Required Synthetic Documents

```text
P-101_Inspection_Report_IR-008.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Compliance_Checklist.pdf
C-201_RUL_Report.pdf
C-201_Inspection_Report.pdf
HX-301_Inspection_Report.pdf
HX-301_Compliance_Checklist.pdf
HX-301_Cleaning_Record.pdf
```

## 22.2 Required Demo JSON Files

```text
assets.json
documents.json
compliance_matrix.json
health_scores.json
knowledge_graph.json
rag_seed_questions.json
```

## 22.3 Required Public Dataset Outputs

Instead of fully training models, the project can use precomputed trend files:

```text
p101_vibration_trend.csv
c201_rul_predictions.csv
hx301_process_trend.csv
```

This is enough for a working hackathon demo.

---

## 23. Dataset Risks and Mitigation

| Risk                                        | Impact                     | Mitigation                                                  |
| ------------------------------------------- | -------------------------- | ----------------------------------------------------------- |
| Public dataset preprocessing takes too long | Model demo delayed         | Use precomputed processed CSV files                         |
| CWRU `.mat` files are difficult to parse    | Pump model delayed         | Use feature CSV generated from limited subset               |
| RAG citations are weak                      | Demo credibility reduced   | Keep synthetic documents short and consistent               |
| LLM gives inconsistent answer               | Demo instability           | Use suggested questions and strict retrieval filtering      |
| HX-301 mapping feels less direct            | Judge may question realism | Clearly state it is process anomaly proxy data              |
| Document upload not ready                   | Demo blocker               | Preload indexed documents                                   |
| OCR not accurate                            | Drawing demo weak          | Use simple clean synthetic drawings with visible asset tags |

---

## 24. Dataset Ethics and Transparency

PlantMind AI must clearly state:

1. Public datasets are used for predictive-maintenance demonstration.
2. Synthetic documents are created for hackathon demo purposes.
3. C-MAPSS is mapped to compressor degradation as a turbomachinery proxy.
4. CWRU bearing data is mapped to pump vibration as a rotating-equipment proxy.
5. Tennessee Eastman Process data is mapped to heat-exchanger-style process anomaly as a process deviation proxy.
6. PlantMind AI is a decision-support system, not a safety-critical autonomous control system.
7. Final maintenance decisions must remain with qualified engineers.

---

## 25. Dataset Acceptance Checklist

Before considering the dataset ready, verify the following:

```text
[ ] All three asset folders exist.
[ ] P-101 documents support high vibration story.
[ ] C-201 documents support decreasing RUL story.
[ ] HX-301 documents support fouling and cleaning evidence story.
[ ] Public dataset outputs are converted into processed CSV files.
[ ] assets.json exists.
[ ] documents.json exists.
[ ] compliance_matrix.json exists.
[ ] health_scores.json exists.
[ ] knowledge_graph.json exists.
[ ] rag_seed_questions.json exists.
[ ] Demo questions return answers with citations.
[ ] Compliance gaps match frozen scope.
[ ] Health scores match frozen scope.
[ ] README clearly states public + synthetic dataset strategy.
```

---

## 26. Final Dataset Scope Statement

PlantMind AI will use three public datasets and one synthetic industrial document pack.

The public datasets provide predictive-maintenance credibility:

```text
NASA C-MAPSS → C-201 Compressor RUL
CWRU Bearing Dataset → P-101 Pump vibration fault detection
Tennessee Eastman Process → HX-301 process anomaly detection
```

The synthetic document pack provides industrial knowledge intelligence:

```text
Maintenance logs
SOPs
Inspection reports
Incident reports
Compliance checklists
Datasheets
Drawings
```

The dataset scope is frozen to three assets only:

```text
P-101 Pump
C-201 Compressor
HX-301 Heat Exchanger
```

This dataset plan supports the final demo story:

```text
Documents + Sensor Trends → Evidence → Asset Risk → RCA → Compliance Gap → Maintenance Recommendation
```

This dataset plan is now frozen.
