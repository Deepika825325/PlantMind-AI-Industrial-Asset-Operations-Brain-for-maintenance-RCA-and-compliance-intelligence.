# NASA C-MAPSS Mapping for PlantMind AI

## Purpose

This folder contains NASA C-MAPSS public dataset files used as a reference for turbomachinery degradation and Remaining Useful Life behavior.

PlantMind AI maps this dataset to the C-201 Process Air Compressor demo use case.

## Selected Dataset for MVP

For the PlantMind AI MVP, only FD001 will be used.

## Why FD001

FD001 is selected because it is the simplest subset:

- 100 training trajectories
- 100 test trajectories
- One operating condition
- One fault mode
- Fault mode: HPC degradation

This makes it suitable for a hackathon MVP and avoids unnecessary complexity.

## PlantMind Asset Mapping

NASA C-MAPSS FD001 is mapped as follows:

| NASA C-MAPSS Concept | PlantMind AI Mapping |
|---|---|
| Engine unit | C-201 Compressor |
| Operational cycle | Compressor operating cycle |
| Sensor measurements | Compressor condition signals |
| RUL value | Estimated remaining useful life |
| Degradation trend | Compressor maintenance risk |

## PlantMind Demo Use

The dataset supports this PlantMind AI story:

C-201 Compressor has a decreasing Remaining Useful Life trend. The system recommends compressor inspection and filter replacement verification during the next maintenance window.

## Files Used

The MVP will use:

```text
train_FD001.txt
test_FD001.txt
RUL_FD001.txt