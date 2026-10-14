
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = PROJECT_ROOT / "qff_basic_benchmark"

sys.path.insert(0, str(BENCHMARK_DIR))

from qiskit import QuantumCircuit, transpile
from qff_basic_benchmark import load_all_models, SHOTS

SEED = 42


def make_bell_circuit(basis):
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
        raise ValueError(f"Unknown basis: {basis}")

    qc.measure([0, 1], [0, 1])
    return qc


def expectation_and_uncertainty(counts):
    shots = sum(counts.values())

    if shots == 0:
        raise ValueError("No measurement counts returned.")

    even = sum(
        count
        for bitstring, count in counts.items()
        if bitstring.replace(" ", "").count("1") % 2 == 0
    )

    expectation = (2 * even - shots) / shots
    uncertainty = math.sqrt(
        max(0.0, 1.0 - expectation**2) / shots
    )

    return expectation, uncertainty


def run_model(name, model):
    print("\n" + "=" * 60)
    print(f"MODEL: {name}")
    print(f"Ports: {model.ports}")
    print(f"Noise source: {model.noise_source}")
    print(f"Shots per circuit: {SHOTS}")

    results = {}

    for basis in ("XX", "YY", "ZZ"):
        circuit = make_bell_circuit(basis)

        compiled = transpile(
            circuit,
            model.backend,
            initial_layout=list(model.ports),
            seed_transpiler=SEED,
        )

        two_qubit_gates = sum(
            1
            for instruction in compiled.data
            if instruction.operation.num_qubits == 2
        )

        print(
            f"{basis}: depth={compiled.depth()}, "
            f"2-qubit gates={two_qubit_gates}"
        )

        for mode, backend in (
            ("ideal", model.ideal_backend),
            ("noisy", model.backend),
        ):
            result = backend.run(
                compiled,
                shots=SHOTS,
                seed_simulator=SEED,
            ).result()

            counts = result.get_counts()
            value, uncertainty = expectation_and_uncertainty(counts)

            results[(mode, basis)] = (value, uncertainty)

    for mode in ("ideal", "noisy"):
        xx, sx = results[(mode, "XX")]
        yy, sy = results[(mode, "YY")]
        zz, sz = results[(mode, "ZZ")]

        fidelity = (1 + xx - yy + zz) / 4
        sigma_f = 0.25 * math.sqrt(
            sx**2 + sy**2 + sz**2
        )
        lower_bound = fidelity - 2 * sigma_f

        print(f"\n{mode.upper()}")
        print(f"XX = {xx:+.5f} +/- {sx:.5f}")
        print(f"YY = {yy:+.5f} +/- {sy:.5f}")
        print(f"ZZ = {zz:+.5f} +/- {sz:.5f}")
        print(f"Fidelity = {fidelity:.5f} +/- {sigma_f:.5f}")
        print(f"F - 2 sigma = {lower_bound:.5f}")
        print(
            "Verification = "
            + ("PASS" if lower_bound > 0.5 else "FAIL")
        )


def main():
    models = load_all_models()

    for name in ("2016", "contemporary", "hyperbolic"):
        run_model(name, models[name])


if __name__ == "__main__":
    main()
