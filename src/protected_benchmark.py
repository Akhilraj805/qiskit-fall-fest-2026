
import math
import sys
from pathlib import Path

from qiskit import QuantumCircuit, transpile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "qff_basic_benchmark"))

from qff_basic_benchmark import load_all_models, SHOTS

SEED = 42

ANCILLA_CANDIDATES = {
    "2016": 1,
    "contemporary": 127,
    "hyperbolic": 1,
}


def make_protected_circuit(basis):
    qc = QuantumCircuit(3, 3)

    # Prepare the Bell state.
    qc.h(0)
    qc.cx(0, 1)

    # Ancilla parity check.
    qc.cx(0, 2)
    qc.cx(1, 2)

    # Rotate into the requested measurement basis.
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

    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def analyze_counts(counts):
    total = sum(counts.values())
    accepted = 0
    correlation_sum = 0

    for bitstring, count in counts.items():
        bits = bitstring.replace(" ", "")[::-1]

        # Keep only shots with ancilla outcome 0.
        if int(bits[2]) == 0:
            accepted += count

            # Correlation is +1 for equal data bits, -1 otherwise.
            correlation_sum += count * (
                1 if int(bits[0]) == int(bits[1]) else -1
            )

    if total == 0:
        raise ValueError("Backend returned no measurement shots.")

    if accepted == 0:
        return None, 0.0, total, 0

    correlation = correlation_sum / accepted
    uncertainty = math.sqrt(
        max(0.0, 1.0 - correlation**2) / accepted
    )

    return correlation, uncertainty, total, accepted


def compile_circuit(circuit, model, ports, ancilla):
    return transpile(
        circuit,
        backend=model.backend,
        initial_layout=[ports[0], ports[1], ancilla],
        seed_transpiler=SEED,
        optimization_level=1,
    )


def run_model(name, model):
    port_a, port_b = model.ports
    ancilla = ANCILLA_CANDIDATES[name]

    print("\n" + "=" * 68)
    print(f"MODEL: {name}")
    print(f"Data ports: {port_a}, {port_b}; ancilla: {ancilla}")
    print(f"Shots per circuit: {SHOTS}")

    # Keep the results separate for each execution mode.
    results = {
        "ideal": {},
        "noisy": {},
    }
    acceptance = {
        "ideal": {},
        "noisy": {},
    }

    for basis in ("XX", "YY", "ZZ"):
        circuit = make_protected_circuit(basis)
        compiled = compile_circuit(
            circuit, model, model.ports, ancilla
        )

        operations = compiled.count_ops()
        two_qubit_gates = sum(
            instruction.operation.num_qubits == 2
            for instruction in compiled.data
        )

        active_qubits = sorted({
            compiled.find_bit(qubit).index
            for instruction in compiled.data
            for qubit in instruction.qubits
        })

        print(
            f"\n{basis}: depth={compiled.depth()}, "
            f"2-qubit gates={two_qubit_gates}, "
            f"active wires={len(active_qubits)}, "
            f"circuit width={compiled.num_qubits}"
        )
        print(f"Native operations: {dict(operations)}")
        print(f"Active physical indices: {active_qubits}")

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
            value, uncertainty, total, accepted = analyze_counts(counts)

            if value is None:
                print(f"  {mode}: no accepted shots")
                continue

            results[mode][basis] = (value, uncertainty)
            acceptance[mode][basis] = accepted / total

            print(
                f"  {mode:5s}: {value:+.5f} +/- {uncertainty:.5f} | "
                f"accepted={accepted / total:.1%} | "
                f"discarded={total - accepted}"
            )

    for mode in ("ideal", "noisy"):
        if not all(
            basis in results[mode]
            for basis in ("XX", "YY", "ZZ")
        ):
            print(f"\n{mode.upper()}: incomplete results; skipping fidelity.")
            continue

        xx, sx = results[mode]["XX"]
        yy, sy = results[mode]["YY"]
        zz, sz = results[mode]["ZZ"]

        fidelity = (1 + xx - yy + zz) / 4
        sigma_f = math.sqrt(sx**2 + sy**2 + sz**2) / 4
        lower_bound = fidelity - 2 * sigma_f

        print("\n" + "-" * 68)
        print(f"{mode.upper()} PROTECTED RESULTS")
        print(f"XX = {xx:+.5f} +/- {sx:.5f}")
        print(f"YY = {yy:+.5f} +/- {sy:.5f}")
        print(f"ZZ = {zz:+.5f} +/- {sz:.5f}")
        print(f"Fidelity = {fidelity:.5f} +/- {sigma_f:.5f}")
        print(f"F - 2*sigma = {lower_bound:.5f}")
        print(
            "Verification = "
            + ("PASS" if lower_bound > 0.5 else "FAIL")
        )

        mean_acceptance = sum(
            acceptance[mode].values()
        ) / len(acceptance[mode])

        print(f"Mean ancilla acceptance: {mean_acceptance:.1%}")


def main():
    models = load_all_models()

    for name in ("2016", "contemporary", "hyperbolic"):
        run_model(name, models[name])


if __name__ == "__main__":
    main()
