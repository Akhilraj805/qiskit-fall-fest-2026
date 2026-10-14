# Geometry-Aware Quantum Entanglement: Basic Track Report

## 1. Problem Statement

Does the physical connectivity of a quantum processor affect how reliably it can create and preserve quantum entanglement?

This project investigates this question using the three processor connectivity models provided in the Qiskit Fall Fest 2026 Basic Track benchmark package.

## 2. Objectives

The objectives are to:

- Compare Bell-state fidelity across different connectivity architectures.
- Evaluate the effect of simulated noise on quantum correlations.
- Investigate parity-based error detection and postselection.
- Compare architectures under a shared synthetic noise model.
- Measure circuit depth and two-qubit gate overhead.
- Study the trade-off between error detection, circuit overhead, and fidelity.
- Develop a hardware/software recommendation based on the experimental results.

## 3. Processor Models

| Model | Description |
|---|---|
| 2016 | Five-qubit reference connectivity graph |
| Contemporary | Larger, calibration-informed connectivity model |
| Hyperbolic | A 35-qubit hyperbolic connectivity graph |

The models represent different connectivity structures and simulation noise assumptions. The native-noise experiment is not a controlled comparison of connectivity alone because the models use different noise assumptions.

## 4. Methodology

### 4.1 Bell-State Preparation

A Bell state is prepared using a Hadamard gate followed by a controlled-NOT gate. Measurements in the XX, YY, and ZZ bases estimate the corresponding quantum correlations.

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

Each measurement basis uses 10,000 shots.

### 4.2 Native-Noise Baseline

The Bell-state experiment is transpiled for each supplied processor model and evaluated using the supplied noisy simulation backend. Ideal simulations provide a reference for comparison.

Circuit depth and two-qubit gate counts are recorded to help characterize the implementation overhead.

### 4.3 Parity-Based Protection

An ancilla qubit is added to perform a parity check. Shots with an ancilla measurement outcome that fails the selected postselection condition are discarded.

The protected experiment evaluates whether postselection improves the estimated Bell-state fidelity.

This is a simple error-detection experiment, not a complete quantum error-correction code. Its additional gates can introduce more noise, and postselection reduces the number of accepted shots.

### 4.4 Common-Noise Comparison

The architectures are also evaluated using the benchmark package's common synthetic noise model.

This experiment helps isolate the behavior of the selected circuit under shared noise assumptions. However, a shared noise model does not eliminate every difference in circuit implementation or account for every source of real hardware noise.

### 4.5 Transpilation and Routing Diagnostic

The protected circuit is transpiled for each architecture using the selected Bell-pair ports and ancilla locations, with `optimization_level=1` and `seed_transpiler=42`.

The diagnostic records circuit depth, two-qubit gate count, final-layout metadata, and the number of instructions literally named `swap`.

A literal SWAP count of zero does not establish that routing incurred no overhead. A compiler can implement routing through other native gates, and final-layout metadata alone is insufficient to determine the exact number of routing SWAP operations.

The diagnostic circuit is also not identical to every measurement-basis circuit used in the full protected experiment. Its depth should therefore not be interpreted as the depth of every protected measurement circuit.

## 5. Results

### 5.1 Native-Noise Baseline

| Model | Fidelity | \(F-2\sigma_F\) | Criterion |
|---|---:|---:|---|
| 2016 | 0.84690 | 0.84166 | Pass |
| Contemporary | 0.94765 | 0.94447 | Pass |
| Hyperbolic | 0.95715 | 0.95427 | Pass |

All three models pass the supplied fidelity criterion in the baseline experiment.

The hyperbolic model has the highest estimated baseline fidelity in these simulations. Because the models use different native-noise assumptions, this result cannot be attributed to connectivity alone.

### 5.2 Parity-Protected Experiment

| Model | Baseline fidelity | Protected fidelity | Mean acceptance |
|---|---:|---:|---:|
| 2016 | 0.84690 | 0.82946 | 90.7% |
| Contemporary | 0.94765 | 0.95698 | 96.7% |
| Hyperbolic | 0.95715 | 0.96502 | 95.9% |

The protected experiment improves estimated fidelity for the Contemporary and Hyperbolic models but reduces it for the 2016 model.

The results demonstrate that postselection does not guarantee an improvement. Its effect depends on the noise, circuit implementation, and errors rejected by the selected parity condition.

Acceptance rates are important because rejected shots do not contribute to the postselected fidelity estimate. Comparisons should therefore consider both fidelity and the number of accepted shots.

### 5.3 Two-Qubit Gate Overhead

| Experiment | Two-qubit gates per basis circuit |
|---|---:|
| Native-noise baseline | 7 |
| Parity-protected experiment | 12 |
| Increase | 5 |

The protected circuits use five additional two-qubit gates per basis circuit in the reported experiments.

These extra operations increase circuit overhead and create additional opportunities for errors. The gate-count difference alone does not establish how many gates were introduced specifically by routing, so it should not be interpreted as an exact routing-SWAP count.

### 5.4 Protected-Circuit Transpilation Diagnostic

| Model | Initial physical-qubit selection | Circuit depth | Two-qubit gates | Literal SWAP instructions |
|---|---|---:|---:|---:|
| 2016 | [0, 4, 1] | 11 | 12 | 0 |
| Contemporary | [126, 129, 127] | 23 | 12 | 0 |
| Hyperbolic | [0, 3, 1] | 23 | 12 | 0 |

These measurements are from the minimal parity-check circuit used in the transpilation diagnostic. They are not a replacement for the separate depth measurements of the XX, YY, and ZZ circuits.

The Contemporary and Hyperbolic diagnostic circuits have greater depth than the 2016 circuit. However, differences in backend instruction sets, connectivity, and transpilation mean that depth alone cannot identify the cause of the difference.

Although the compiled circuits contain no instructions literally named `swap`, routing may still have been implemented using native gates. An exact routing-overhead comparison requires a routing-stage or compiler-metadata analysis that explicitly identifies routing operations.

### 5.5 Common-Noise Experiment

| Model | Fidelity | \(F-2\sigma_F\) | Depths (XX, YY, ZZ) |
|---|---:|---:|---|
| 2016 | 0.95715 | 0.95427 | 14, 14, 14 |
| Contemporary | 0.95715 | 0.95427 | 14, 14, 14 |
| Hyperbolic | 0.95715 | 0.95427 | 14, 14, 14 |

The identical results occurred for the selected circuits under this particular synthetic noise experiment.

They do not establish that the three architectures are generally equivalent. Instead, the results reflect the selected circuit structure and common noise assumptions.

The common-noise experiment is a useful controlled comparison, but it does not capture every hardware-dependent effect, such as architecture-specific calibration variation or idle-qubit decoherence.

## 6. Architecture Diagrams

The generated diagrams are available at:

- `results/architecture_diagrams/2016_architecture.png`
- `results/architecture_diagrams/contemporary_architecture.png`
- `results/architecture_diagrams/hyperbolic_architecture.png`

The Contemporary graph is drawn using a force-directed visualization layout. Its plotted positions are for readability and are not a representation of actual physical chip coordinates.

The diagrams illustrate the connectivity graphs supplied by the benchmark package.

## 7. Discussion

The native-noise baseline shows different fidelity estimates across the supplied processor models. The Hyperbolic model achieves the highest baseline fidelity in the measured simulations, but differences in noise assumptions prevent a connectivity-only conclusion.

The parity-protected experiment produces mixed results. Fidelity increases for the Contemporary and Hyperbolic models but decreases for the 2016 model. The additional two-qubit gates and postselection cost show why an error-detection technique must be evaluated using both its potential fidelity benefit and its implementation overhead.

The common-noise experiment produces identical fidelity estimates for the selected circuits. This emphasizes the importance of experimental controls when investigating whether connectivity or noise assumptions explain performance differences.

### Hardware and Software Recommendation

A useful improvement is a **routing-aware, noise-aware compilation strategy** for parity-protected Bell-state experiments.

The compiler should consider:

1. **Connectivity:** Prefer ancilla locations that support the required interactions with minimal routing overhead.
2. **Gate reliability:** Consider calibrated two-qubit gate error rates when selecting a circuit layout.
3. **Circuit cost:** Evaluate entangling-gate count and circuit depth alongside fidelity.
4. **Postselection efficiency:** Measure acceptance rate as well as the fidelity calculated from accepted shots.
5. **Architecture-specific benefit:** Enable parity protection only when experimental evidence shows that its fidelity benefit justifies its added overhead.

This recommendation follows from the mixed results of the parity experiment and the observed increase from seven to twelve two-qubit gates. The current experiments motivate this strategy but do not yet demonstrate that a new compiler achieves better results.

## 8. Limitations

- All reported results are from simulation, not live quantum hardware.
- The supplied models use different native-noise assumptions in the baseline experiment.
- The common-noise experiment uses a synthetic model and does not represent every source of real hardware noise.
- A single parity measurement does not detect or correct every possible error.
- Postselection reduces the number of accepted shots and must be considered when comparing fidelity estimates.
- The common-noise result applies to the selected circuit and noise setup; it is not a universal architecture ranking.
- The transpilation diagnostic reports circuit depth, two-qubit gate count, and literal SWAP instructions, but it does not establish an exact routing-SWAP count.
- The experiments do not yet demonstrate a new routing-aware compiler or a live-hardware improvement.

## 9. Conclusion

This project evaluates Bell-state preparation across three supplied quantum processor connectivity models using native-noise simulations, parity-based postselection, and a common synthetic noise comparison.

All three baseline simulations pass the benchmark's fidelity criterion. The Hyperbolic model has the highest baseline fidelity in the measured results. Parity-based protection improves the estimated fidelity for two models but not the 2016 model, illustrating the trade-off between error detection and circuit overhead.

The protected experiment uses five additional two-qubit gates per basis circuit. The transpilation diagnostic also shows that circuit depth differs across the selected processor models, while the absence of literal SWAP instructions is insufficient to establish zero routing overhead.

Overall, the experiments show why quantum processor architecture should be evaluated together with routing, noise assumptions, circuit structure, and measurement methodology. They motivate a compiler strategy that jointly considers connectivity, calibrated gate reliability, circuit overhead, and postselection efficiency.

## 10. Reproducibility

The supplied benchmark definitions remain unchanged. Experiment scripts, text outputs, and architecture diagrams are included in the repository.

The reported numerical values correspond to the saved simulation outputs. The simulations use 10,000 shots per measurement basis and the recorded transpilation settings. All results should be interpreted as simulation evidence rather than measurements from physical quantum hardware.

The main experiment runner is `main.py`. The individual scripts can also be run separately to reproduce the baseline, protected, and common-noise experiments.
