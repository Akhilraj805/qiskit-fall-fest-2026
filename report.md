# Geometry-Aware Quantum Entanglement: Basic Track Report

## 1. Problem Statement

Does the physical connectivity of a quantum processor affect how reliably it can create and preserve quantum entanglement?

This project investigates the question using the three processor connectivity models provided in the Qiskit Fall Fest 2026 Basic Track benchmark package.

## 2. Objective

The objectives are to:

- Compare Bell-state fidelity across different connectivity architectures.
- Evaluate the effect of simulated noise on quantum correlations.
- Investigate parity-based error detection and postselection.
- Compare architectures under a shared synthetic noise model.
- Understand the trade-off between circuit overhead and fidelity.

## 3. Processor Models

| Model | Description |
|---|---|
| 2016 | Five-qubit reference connectivity graph |
| Contemporary | Larger, calibration-informed connectivity model |
| Hyperbolic | A 35-qubit hyperbolic connectivity graph |

The models represent different connectivity structures and simulation noise assumptions. They should not be treated as a controlled comparison of connectivity alone in the native-noise experiment.

## 4. Methodology

### 4.1 Bell-State Preparation

A Bell state is prepared using a Hadamard gate followed by a controlled-NOT gate. The resulting state is measured in the XX, YY, and ZZ bases to estimate its correlations.

The fidelity estimate is:

\[
F=\frac{1+XX-YY+ZZ}{4}
\]

The uncertainty is estimated as:

\[
\sigma_F=\frac{1}{4}\sqrt{\sigma_{XX}^2+\sigma_{YY}^2+\sigma_{ZZ}^2}
\]

The benchmark pass criterion is:

\[
F-2\sigma_F>0.5
\]

### 4.2 Native-Noise Baseline

The Bell-state experiment is transpiled for each supplied processor model and evaluated on its noisy and ideal simulation backends. Each measurement basis uses 10,000 shots.

### 4.3 Parity-Based Protection

An ancilla qubit is used for a parity measurement. Shots with an ancilla measurement outcome that fails the selected postselection condition are discarded.

This experiment explores a simple error-detection technique; it is not a complete quantum error-correction code.

### 4.4 Common-Noise Comparison

The architectures are also evaluated using a common synthetic noise model. This helps examine architecture connectivity under more controlled simulation conditions.

## 5. Results

### 5.1 Native-Noise Baseline

| Model | Fidelity | \(F-2\sigma_F\) | Criterion |
|---|---:|---:|---|
| 2016 | 0.84690 | 0.84166 | Pass |
| Contemporary | 0.94765 | 0.94447 | Pass |
| Hyperbolic | 0.95715 | 0.95427 | Pass |

All three models pass the supplied fidelity criterion in the baseline experiment. The hyperbolic model has the highest estimated baseline fidelity in these simulations.

### 5.2 Parity-Protected Experiment

| Model | Baseline fidelity | Protected fidelity | Mean acceptance |
|---|---:|---:|---:|
| 2016 | 0.84690 | 0.82946 | 90.7% |
| Contemporary | 0.94765 | 0.95698 | 96.7% |
| Hyperbolic | 0.95715 | 0.96502 | 95.9% |

The protected experiment improves estimated fidelity for the contemporary and hyperbolic models, but reduces it for the 2016 model. The results demonstrate that postselection does not guarantee an improvement: the outcome depends on the noise and the additional circuit operations.

The acceptance rates matter because rejected shots do not contribute to the postselected fidelity estimate. The protected circuit also introduces additional two-qubit operations.

### 5.3 Common-Noise Experiment

| Model | Fidelity | \(F-2\sigma_F\) | Depths (XX, YY, ZZ) |
|---|---:|---:|---|
| 2016 | 0.95715 | 0.95427 | 14, 14, 14 |
| Contemporary | 0.95715 | 0.95427 | 14, 14, 14 |
| Hyperbolic | 0.95715 | 0.95427 | 14, 14, 14 |

The identical results occurred for the selected circuits under this particular synthetic noise experiment. They do not establish that the three architectures are generally equivalent. The result reflects the selected circuit structure and common noise assumptions.

## 6. Architecture Diagrams

The generated diagrams are available at:

- `results/architecture_diagrams/2016_architecture.png`
- `results/architecture_diagrams/contemporary_architecture.png`
- `results/architecture_diagrams/hyperbolic_architecture.png`

The contemporary graph is drawn using a force-directed visualization layout. Its plotted positions are for readability and are not a representation of physical chip coordinates.

## 7. Discussion

The baseline simulations show different fidelity estimates across the supplied models. The parity experiment shows that additional error-detection operations and postselection can help in some cases but can also reduce fidelity. The common-noise experiment produces identical estimates for the selected circuits, highlighting the importance of experimental controls when attributing performance differences to architecture.

The results support evaluating connectivity together with routing overhead, gate noise, measurement noise, and the details of the circuit being executed.

## 8. Limitations

- All reported results are from simulation, not live quantum hardware.
- The supplied models use different native-noise assumptions in the baseline experiment.
- The common-noise experiment uses a synthetic noise model and does not represent every source of real hardware noise.
- A single parity measurement does not correct every possible error.
- Postselection reduces the number of accepted shots and must be considered when comparing fidelity estimates.
- The common-noise result applies to the selected circuit and noise setup; it is not a universal architecture ranking.

## 9. Conclusion

This project evaluates Bell-state preparation across three supplied quantum processor connectivity models using native-noise simulations, parity-based postselection, and a common synthetic noise comparison.

All three baseline simulations pass the benchmark's fidelity criterion. The hyperbolic model has the highest baseline fidelity in the measured results. Parity-based protection improves the estimated fidelity for two models but not the 2016 model, illustrating the trade-off between error detection and circuit overhead.

The experiments show why quantum processor architecture should be evaluated together with routing, noise assumptions, circuit structure, and measurement methodology.

## 10. Reproducibility

The supplied benchmark definitions remain unchanged. Experiment scripts, text outputs, and architecture diagrams are included in the repository. The reported values correspond to the saved simulation outputs.