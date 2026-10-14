
import math
import sys
from pathlib import Path

from qiskit import QuantumCircuit, transpile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "qff_basic_benchmark"))

from qff_basic_benchmark import load_all_models, SHOTS


SEED = 42


def make_bell_circuit(basis):
    """Prepare a Bell state and rotate measurements into the requested basis."""
    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    if basis == "XX":
        qc.h(0)
        qc.h(1)
    elif basis == "YY":
        qc.sdg(0)
        qc.h(0)
        qc.sdg(1)
        qc.h(1)
    elif basis != "ZZ":
        raise ValueError(f"Unsupported basis: {basis}")

    qc.measure([0, 1], [0, 1])
    return qc


def calculate_correlation(counts):
    """Calculate the measured two-qubit correlation and its standard error."""
    total_shots = sum(counts.values())

    if total_shots == 0:
        raise ValueError("No measurement results were returned.")

    correlation_sum = 0

    for bitstring, count in counts.items():
        bits = bitstring.replace(" ", "")[::-1]
        parity = 1 if bits[0] == bits[1] else -1
        correlation_sum += parity * count

    correlation = correlation_sum / total_shots
    uncertainty = math.sqrt(
        max(0.0, 1.0 - correlation**2) / total_shots
    )

    return correlation, uncertainty


def calculate_fidelity(correlations, uncertainties):
    """Estimate Bell-state fidelity and propagated uncertainty."""
    xx = correlations["XX"]
    yy = correlations["YY"]
    zz = correlations["ZZ"]

    fidelity = (1 + xx - yy + zz) / 4

    sigma = 0.25 * math.sqrt(
        uncertainties["XX"] ** 2
        + uncertainties["YY"] ** 2
        + uncertainties["ZZ"] ** 2
    )

    return fidelity, sigma


def count_two_qubit_gates(compiled):
    return sum(
        instruction.operation.num_qubits == 2
        for instruction in compiled.data
        if instruction.operation.name not in ("barrier",)
    )


def run_experiment(model, backend, seed):
    correlations = {}
    uncertainties = {}
    depths = []
    gate_counts = []
    active_qubits = set()

    for basis in ("XX", "YY", "ZZ"):
        circuit = make_bell_circuit(basis)

        compiled = transpile(
            circuit,
            backend=model.backend,
            initial_layout=list(model.ports),
            seed_transpiler=SEED,
            optimization_level=1,
        )

        print(f"\n  Basis: {basis}")
        print("  Transpiled circuit:")
        print(compiled.draw(output="text", fold=100))
        print("  Operations:", compiled.count_ops())
        print("  Layout:", compiled.layout)

        depths.append(compiled.depth())
        gate_counts.append(count_two_qubit_gates(compiled))

        for instruction in compiled.data:
            if instruction.operation.name in ("barrier", "measure"):
                continue
            for qubit in instruction.qubits:
                active_qubits.add(compiled.find_bit(qubit).index)

        result = backend.run(
            compiled,
            shots=SHOTS,
            seed_simulator=seed,
        ).result()

        corr, sigma = calculate_correlation(
            result.get_counts()
        )

        correlations[basis] = corr
        uncertainties[basis] = sigma

    fidelity, sigma_f = calculate_fidelity(
        correlations, uncertainties
    )

    return {
        "correlations": correlations,
        "uncertainties": uncertainties,
        "fidelity": fidelity,
        "sigma_f": sigma_f,
        "lower_bound": fidelity - 2 * sigma_f,
        "depths": depths,
        "two_qubit_gates": gate_counts,
        "active_qubits": sorted(active_qubits),
    }


def main():
    models = load_all_models(noise="common")

    print("=" * 72)
    print("QISKIT FALL FEST 2026 - COMMON-NOISE BASELINE")
    print(f"Shots per measurement basis: {SHOTS}")
    print(f"Transpiler seed: {SEED}")
    print("=" * 72)

    for name, model in models.items():
        print(f"\nMODEL: {name}")
        print(f"Ports: {model.ports}")
        print(f"Noise source: {model.noise_source}")

        ideal = run_experiment(
            model, model.ideal_backend, SEED
        )
        noisy = run_experiment(
            model, model.backend, SEED
        )

        print("\nIdeal correlations:")
        for basis, value in ideal["correlations"].items():
            print(f"  {basis}: {value:+.5f}")

        print(
            f"Ideal fidelity: {ideal['fidelity']:.5f}"
            f" +/- {ideal['sigma_f']:.5f}"
        )

        print("\nCommon-noise correlations:")
        for basis in ("XX", "YY", "ZZ"):
            corr = noisy["correlations"][basis]
            sigma = noisy["uncertainties"][basis]
            print(f"  {basis}: {corr:+.5f} +/- {sigma:.5f}")

        print(
            f"Common-noise fidelity: {noisy['fidelity']:.5f}"
            f" +/- {noisy['sigma_f']:.5f}"
        )
        print(f"F - 2 sigma_F: {noisy['lower_bound']:.5f}")
        print(f"Verification threshold passed: {noisy['lower_bound'] > 0.5}")
        print(f"Circuit depths (XX, YY, ZZ): {noisy['depths']}")
        print(f"Two-qubit gates (XX, YY, ZZ): {noisy['two_qubit_gates']}")
        print(f"Active physical qubits: {noisy['active_qubits']}")


if __name__ == "__main__":
    main()

