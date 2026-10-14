from math import sqrt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
)

SHOTS = 4096
SEED = 42


def build_noise_model():
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


def build_circuit(basis, protected):
    if protected:
        qc = QuantumCircuit(3, 3)
    else:
        qc = QuantumCircuit(2, 2)

    # Prepare the Bell state on qubits 0 and 1.
    qc.h(0)
    qc.cx(0, 1)

    # ZZ parity check: ancilla records whether the bits differ.
    if protected:
        qc.cx(0, 2)
        qc.cx(1, 2)

    # Rotate the Bell qubits for the requested measurement.
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

    qc.measure(0, 0)
    qc.measure(1, 1)

    if protected:
        qc.measure(2, 2)

    return qc


def run_case(protected):
    simulator = AerSimulator(noise_model=build_noise_model())
    accepted_counts = {}
    accepted_shots = 0

    for basis in ("XX", "YY", "ZZ"):
        circuit = build_circuit(basis, protected)
        compiled = transpile(
            circuit,
            basis_gates=["u", "cx"],
            optimization_level=1,
            seed_transpiler=SEED,
        )

        result = simulator.run(
            compiled,
            shots=SHOTS,
            seed_simulator=SEED,
        ).result()

        counts = result.get_counts()
        filtered = {}

        for bitstring, count in counts.items():
            bits = bitstring.replace(" ", "")

            # Classical bit 2 is the ancilla result.
            # Qiskit displays classical bit 2 at the left.
            if not protected or bits[0] == "0":
                data_bits = bits[-2:]
                filtered[data_bits] = (
                    filtered.get(data_bits, 0) + count
                )

        accepted_counts[basis] = filtered
        accepted_shots += sum(filtered.values())

    correlations = {}

    for basis, counts in accepted_counts.items():
        total = sum(counts.values())

        if total == 0:
            raise ValueError(
                f"No accepted shots for {basis}; cannot estimate fidelity."
            )

        even = sum(
            count
            for bits, count in counts.items()
            if bits.count("1") % 2 == 0
        )

        value = (2 * even - total) / total
        uncertainty = sqrt(max(0.0, 1 - value**2) / total)

        correlations[basis] = value
        correlations[basis + "_sigma"] = uncertainty

    xx = correlations["XX"]
    yy = correlations["YY"]
    zz = correlations["ZZ"]

    fidelity = (1 + xx - yy + zz) / 4

    sigma_f = 0.25 * sqrt(
        correlations["XX_sigma"] ** 2
        + correlations["YY_sigma"] ** 2
        + correlations["ZZ_sigma"] ** 2
    )

    acceptance = accepted_shots / (SHOTS * 3)

    print("\nProtected:" if protected else "\nUnprotected:")
    print(f"XX = {xx:.4f}")
    print(f"YY = {yy:.4f}")
    print(f"ZZ = {zz:.4f}")
    print(f"Fidelity = {fidelity:.4f} ± {sigma_f:.4f}")
    print(f"F - 2 sigma = {fidelity - 2 * sigma_f:.4f}")
    print(f"Acceptance rate = {acceptance:.2%}")


if __name__ == "__main__":
    print("Illustrative noise model; not official hardware results.")
    run_case(protected=False)
    run_case(protected=True)
