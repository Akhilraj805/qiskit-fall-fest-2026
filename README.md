# Qiskit Fall Fest 2026 — Basic Track

## Project Overview

This project investigates how quantum processor connectivity affects the reliability of preparing and measuring entangled Bell states.

Using the supplied Qiskit Fall Fest Basic Track benchmark package, we evaluate three processor connectivity models:

- **2016:** A five-qubit reference architecture.
- **Contemporary:** A larger, calibration-informed processor connectivity model.
- **Hyperbolic:** A 35-qubit hyperbolic connectivity model.

The experiments use Qiskit and simulated quantum backends to compare baseline Bell-state fidelity, parity-based protection, and a common-noise experiment.

## Objectives

- Compare Bell-state fidelity across the three supplied architectures.
- Evaluate ideal and noisy simulation results.
- Investigate parity-based error detection and postselection.
- Compare architectures under a common synthetic noise model.
- Identify the trade-offs between connectivity, circuit overhead, and fidelity.

## Repository Structure

```text
qiskit-fall-fest/
├── qff_basic_benchmark/       # Supplied benchmark package
├── src/                       # Experiment and diagram-generation scripts
├── configs/                   # Configuration notes
├── results/
│   ├── architecture_diagrams/
│   ├── official_baseline_output.txt
│   ├── protected_benchmark_output.txt
│   └── results_summary.txt
├── test_qiskit.py
├── README.md
├── report.md
└── main.py
```

## Experiments

1. **Native-noise baseline:** Measures Bell-state correlations and estimates fidelity using each supplied model's noisy and ideal simulation backends.
2. **Parity-protected experiment:** Uses an ancilla parity measurement and postselection to study the effect of a simple error-detection strategy.
3. **Common-noise experiment:** Applies a common synthetic noise model to compare the architectures under more controlled conditions.

All experiments use 10,000 shots per measurement basis.

## Preliminary Results

| Architecture | Baseline fidelity | Protected fidelity |
|---|---:|---:|
| 2016 | 0.84690 | 0.82946 |
| Contemporary | 0.94765 | 0.95698 |
| Hyperbolic | 0.95715 | 0.96502 |

These are simulated results, not measurements from live quantum hardware. The parity-protected results use postselection, so they must be interpreted alongside their acceptance rates and additional circuit overhead.

## Architecture Diagrams

- [2016 architecture](results/architecture_diagrams/2016_architecture.png)
- [Contemporary architecture](results/architecture_diagrams/contemporary_architecture.png)
- [Hyperbolic architecture](results/architecture_diagrams/hyperbolic_architecture.png)

The contemporary diagram uses a force-directed layout for visualization. Its graph connectivity comes from the supplied benchmark model; the plotted positions should not be interpreted as the processor's physical chip layout.

## Requirements

- Python
- Qiskit and Qiskit Aer
- Dependencies listed in `qff_basic_benchmark/requirements.txt`

Run the experiments from the project root using the instructions provided with the scripts. A unified runner will be added to simplify execution.

## Limitations

- Results are based on simulation.
- Parity detection adds circuit overhead and discards shots that fail the postselection condition.
- A single parity check is not a complete quantum error-correction code.
- The common-noise experiment represents a controlled synthetic comparison, not the full noise characteristics of real processors.

## Reproducibility

The benchmark definitions supplied for the nine core cases are retained unchanged. Experiment scripts and result summaries are included to support reproducibility and review.