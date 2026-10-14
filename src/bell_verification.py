
from math import sqrt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError,
)

SHOTS = 4096
SEED = 42


def build_bell_circuit(basis):
    """Prepare |Phi+> and measure XX, YY, or ZZ."""
    circuit = QuantumCircuit(2, 2)

    # Bell-state preparation
    circuit.h(0)
    circuit.cx(0, 1)

    # Rotate the measurement basis to measure the requested Pauli pair
    if basis == "XX":
        circuit.h(0)
        circuit.h(1)
    elif basis == "YY":
        circuit.sdg(0)
        circuit.sdg(1)
        circuit.h(0)
        circuit.h(1)
    elif basis != "ZZ":
        raise ValueError(f"Unsupported basis: {basis}")

    circuit.measure([0, 1], [0, 1])
    return circuit


def build_illustrative_noise_model():
    """Example noise only; replace with official parameters when provided."""
    noise = NoiseModel()

    # Illustrative error probabilities, NOT official hardware specifications
    one_qubit_error = depolarizing_error(0.001, 1)
    two_qubit_error = depolarizing_error(0.02, 2)

    readout_error = ReadoutError([
        [0.99, 0.01],
        [0.01, 0.99],
    ])

    noise.add_all_qubit_quantum_error(one_qubit_error, ["u"])
    noise.add_all_qubit_quantum_error(two_qubit_error, ["cx"])
    noise.add_all_qubit_readout_error(readout_error)

    return noise


def correlation_from_counts(counts):
    """Estimate <PP> using the parity of each two-bit outcome."""
    total = sum(counts.values())
    if total == 0:
        raise ValueError("No measurement shots were returned.")

    even = sum(
        count
        for bitstring, count in counts.items()
        if bitstring.replace(" ", "").count("1") % 2 == 0
    )

    odd = total - even
    expectation = (even - odd) / total

    # Standard error for a ±1-valued measurement
    uncertainty = sqrt(max(0.0, 1 - expectation**2) / total)

    return expectation, uncertainty


def run_verification(noisy=False):
    noise = build_illustrative_noise_model() if noisy else None
    simulator = AerSimulator(noise_model=noise)

    correlations = {}

    for basis in ["XX", "YY", "ZZ"]:
        circuit = build_bell_circuit(basis)

        compiled = transpile(
            circuit,
            simulator,
            seed_transpiler=SEED,
            optimization_level=1,
        )

        result = simulator.run(
            compiled,
            shots=SHOTS,
            seed_simulator=SEED,
        ).result()

        counts = result.get_counts()
        expectation, uncertainty = correlation_from_counts(counts)

        correlations[basis] = expectation
        correlations[basis + "_uncertainty"] = uncertainty

    xx = correlations["XX"]
    yy = correlations["YY"]
    zz = correlations["ZZ"]

    fidelity = (1 + xx - yy + zz) / 4

    sigma_f = 0.25 * sqrt(
        correlations["XX_uncertainty"] ** 2
        + correlations["YY_uncertainty"] ** 2
        + correlations["ZZ_uncertainty"] ** 2
    )

    lower_bound = fidelity - 2 * sigma_f

    print("\n" + "=" * 45)
    print("BELL-STATE VERIFICATION")
    print("Mode:", "ILLUSTRATIVE NOISY" if noisy else "IDEAL")
    print("Shots per measurement basis:", SHOTS)
    print("-" * 45)

    for basis in ["XX", "YY", "ZZ"]:
        print(
            f"<{basis}> = {correlations[basis]:+.5f} "
            f"+/- {correlations[basis + '_uncertainty']:.5f}"
        )

    print("-" * 45)
    print(f"Bell fidelity F:       {fidelity:.5f}")
    print(f"Fidelity uncertainty:  {sigma_f:.5f}")
    print(f"F - 2*sigma_F:         {lower_bound:.5f}")
    print(
        "Bell verification:",
        "PASS" if lower_bound > 0.5 else "NOT VERIFIED",
    )


if __name__ == "__main__":
    run_verification(noisy=False)
    run_verification(noisy=True)
