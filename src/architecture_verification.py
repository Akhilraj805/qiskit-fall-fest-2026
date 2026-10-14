from math import sqrt

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
)

from architectures import ARCHITECTURES


SHOTS = 4096
SEED = 42
BASIS = ("XX", "YY", "ZZ")


def build_noise_model():
    """Illustrative noise only; replace with official parameters."""
    noise = NoiseModel()

    noise.add_all_qubit_quantum_error(
        depolarizing_error(0.001, 1), ["u"]
    )
    noise.add_all_qubit_quantum_error(
        depolarizing_error(0.02, 2), ["cx"]
    )
    noise.add_all_qubit_readout_error(
        ReadoutError([[0.99, 0.01], [0.01, 0.99]])
    )

    return noise


def build_bell_circuit(basis):
    """Prepare |Phi+>, rotate measurement basis, then measure."""
    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    if basis == "XX":
        qc.h(0)
        qc.h(1)
    elif basis == "YY":
        qc.sdg(0)
        qc.sdg(1)
        qc.h(0)
        qc.h(1)
    elif basis != "ZZ":
        raise ValueError(f"Unsupported basis: {basis}")

    qc.measure([0, 1], [0, 1])
    return qc


def correlation(counts):
    total = sum(counts.values())
    if total == 0:
        raise ValueError("No measurement shots were returned.")

    even = sum(
        count
        for bits, count in counts.items()
        if bits.replace(" ", "").count("1") % 2 == 0
    )
    expectation = (2 * even - total) / total
    uncertainty = sqrt(max(0.0, 1 - expectation**2) / total)

    return expectation, uncertainty


def run_architecture(name, config, noisy):
    edges = config["edges"]
    ports = config["ports"]
    num_qubits = config["num_qubits"]

    # Treat the supplied graph edges as undirected couplings.
    directed_edges = edges + [(v, u) for u, v in edges]
    coupling_map = CouplingMap(
    couplinglist=directed_edges
    )

    noise = build_noise_model() if noisy else None
    simulator = AerSimulator(noise_model=noise)

    results = {}
    circuit_depths = []
    two_qubit_counts = []
    explicit_swaps = []

    for basis in BASIS:
        logical_circuit = build_bell_circuit(basis)

        compiled = transpile(
            logical_circuit,
            coupling_map=coupling_map,
            initial_layout=list(ports),
            basis_gates=["u", "cx"],
            optimization_level=1,
            seed_transpiler=SEED,
        )

        job = simulator.run(
            compiled,
            shots=SHOTS,
            seed_simulator=SEED,
        )
        counts = job.result().get_counts()

        value, uncertainty = correlation(counts)
        results[basis] = value
        results[basis + "_sigma"] = uncertainty

        circuit_depths.append(compiled.depth())
        two_qubit_counts.append(
            sum(
                1
                for instruction in compiled.data
                if instruction.operation.num_qubits == 2
            )
        )
        explicit_swaps.append(
            sum(
                1 for instruction in compiled.data
                if instruction.operation.name == "swap"
            )
        )

    xx = results["XX"]
    yy = results["YY"]
    zz = results["ZZ"]

    fidelity = (1 + xx - yy + zz) / 4
    sigma_f = 0.25 * sqrt(
        results["XX_sigma"] ** 2
        + results["YY_sigma"] ** 2
        + results["ZZ_sigma"] ** 2
    )
    lower_bound = fidelity - 2 * sigma_f

    return {
        "architecture": name,
        "mode": "noisy" if noisy else "ideal",
        "fidelity": fidelity,
        "sigma_f": sigma_f,
        "lower_bound": lower_bound,
        "passes": lower_bound > 0.5,
        "max_depth": max(circuit_depths),
        "total_2q_gates": sum(two_qubit_counts),
        "explicit_swaps": sum(explicit_swaps),
        "configured_qubits": num_qubits,
        "ports": ports,
    }


def main():
    print("ARCHITECTURE-AWARE BELL-STATE BENCHMARK")
    print("WARNING: illustrative graphs and noise; not official results.")

    for name, config in ARCHITECTURES.items():
        for noisy in (False, True):
            result = run_architecture(name, config, noisy)

            print("\n" + "-" * 55)
            for key, value in result.items():
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
