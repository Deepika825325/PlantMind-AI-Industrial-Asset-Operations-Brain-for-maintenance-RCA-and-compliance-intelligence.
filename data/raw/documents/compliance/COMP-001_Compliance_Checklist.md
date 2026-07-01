# COMP-001: PlantMind Demo Compliance Checklist

Document ID: COMP-001
Document Type: Compliance Checklist
Assets Covered: P-101, C-201, HX-301
Review Date: 2026-03-10
Reviewer: Demo Compliance Officer
Checklist Status: Open Gaps Found

---

## 1. Compliance Context

This checklist evaluates whether required maintenance, inspection, safety, and evidence records are available for PlantMind demo assets.

The compliance logic is inspired by industrial maintenance safety practices, including:

* Work permit discipline
* Lockout tagout evidence
* Inspection evidence
* Maintenance verification
* Cleaning records
* Safe shutdown procedure availability
* Asset-specific evidence tracking

This checklist is synthetic demo data and is not a replacement for any official safety standard.

---

## 2. Assets Covered

| Asset ID | Asset Name                     | Asset Type     | Criticality |
| -------- | ------------------------------ | -------------- | ----------- |
| P-101    | Cooling Water Circulation Pump | Pump           | High        |
| C-201    | Process Air Compressor         | Compressor     | Medium-High |
| HX-301   | Feed Preheater Heat Exchanger  | Heat Exchanger | Medium      |

---

## 3. Compliance Matrix

| Asset ID | Requirement                           | Expected Evidence             | Status    | Evidence File | Gap |
| -------- | ------------------------------------- | ----------------------------- | --------- | ------------- | --- |
| P-101    | Weekly vibration inspection           | Inspection report             | Available | IR-P101-001   | No  |
| P-101    | Weekly lubrication check              | Lubrication record            | Missing   | Not available | Yes |
| P-101    | Work permit before bearing inspection | Work permit record            | Missing   | Not available | Yes |
| C-201    | Monthly compressor inspection         | Inspection report             | Available | IR-C201-001   | No  |
| C-201    | Filter replacement verification       | Maintenance log or work order | Delayed   | WO-1003       | Yes |
| C-201    | Safe shutdown procedure confirmation  | SOP reference                 | Available | SOP-C201-001  | No  |
| HX-301   | Pressure test evidence                | Test record or SOP reference  | Available | SOP-HX301-001 | No  |
| HX-301   | Cleaning and fouling inspection       | Cleaning record               | Overdue   | Not available | Yes |
| HX-301   | Work permit before cleaning           | Work permit record            | Missing   | Not available | Yes |

---

## 4. Ground Truth Compliance Gaps

The following compliance gaps are intentionally defined for the demo:

1. P-101 lubrication evidence is missing.
2. P-101 work permit evidence is missing before bearing inspection.
3. C-201 filter replacement verification is delayed.
4. HX-301 cleaning and fouling inspection evidence is overdue.
5. HX-301 work permit evidence is missing before cleaning activity.

---

## 5. Asset-Level Compliance Summary

### P-101 Pump

P-101 has two compliance gaps:

* Weekly lubrication evidence is missing.
* Work permit evidence is missing before bearing inspection.

P-101 also has technical risk because vibration exceeded the critical threshold.

### C-201 Compressor

C-201 has one compliance gap:

* Filter replacement verification is delayed.

Monthly compressor inspection evidence is available.

### HX-301 Heat Exchanger

HX-301 has two compliance gaps:

* Cleaning and fouling inspection evidence is overdue.
* Work permit evidence is missing before cleaning activity.

HX-301 also has technical risk because outlet temperature is below target and pressure drop is above warning threshold.

---

## 6. Recommended Compliance Actions

| Gap                                | Recommended Action                                         |
| ---------------------------------- | ---------------------------------------------------------- |
| P-101 lubrication evidence missing | Perform lubrication check and upload lubrication record    |
| P-101 work permit missing          | Create or attach work permit before bearing inspection     |
| C-201 filter verification delayed  | Verify filter replacement completion and update work order |
| HX-301 cleaning evidence overdue   | Schedule cleaning inspection and upload cleaning record    |
| HX-301 work permit missing         | Create or attach work permit before cleaning activity      |

---

## 7. Related Documents

* SOP-GEN-001: Work Permit and Lockout Tagout Requirements
* SOP-P101-001: Pump Lubrication and Bearing Check
* SOP-P101-002: Pump Vibration Inspection
* SOP-C201-001: Compressor Safe Shutdown and Inspection Preparation
* SOP-HX301-001: Heat Exchanger Cleaning and Fouling Check
* IR-P101-001: Pump Vibration Inspection
* IR-C201-001: Compressor Monthly Inspection
* IR-HX301-001: Heat Exchanger Performance Inspection
* IR-GEN-001: Safety Evidence Audit
* work_orders.csv
* ground_truth_compliance_gaps.csv

---

## 8. Keywords

compliance, compliance checklist, missing evidence, overdue evidence, delayed verification, work permit, LOTO, lubrication evidence, cleaning evidence, filter replacement, P-101, C-201, HX-301
