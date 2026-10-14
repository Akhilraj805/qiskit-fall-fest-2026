
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

from architectures import ARCHITECTURES, validate_architectures


def create_bell_circuit():
    """Prepare a Bell state on two logical qubits."""
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit


def benchmark_architecture(name, config):
    # Make each listed connection usable in either direction.
    directed_edges = []
    for u, v in config["edges"]:
        directed_edges.extend([(u, v), (v, u)])

    coupling_map = CouplingMap(
        couplinglist=directed_edges
    )

    bell_circuit = create_bell_circuit()
    port_a, port_b = config["ports"]

    compiled = transpile(
        bell_circuit,
        coupling_map=coupling_map,
        initial_layout=[port_a, port_b],
        basis_gates=["u", "cx"],
        optimization_level=1,
        seed_transpiler=42,
    )

    # Count the physical qubits appearing in actual operations.
    active_qubits = set()
    two_qubit_gates = 0
    swap_count = 0

    for instruction in compiled.data:
        operation = instruction.operation
        qubits = instruction.qubits

        if operation.name != "barrier":
            for qubit in qubits:
                active_qubits.add(compiled.find_bit(qubit).index)

        if operation.num_qubits == 2:
            two_qubit_gates += 1

        if operation.name == "swap":
            swap_count += 1

    print(f"\n--- {name} ---")
    print(f"Description: {config['description']}")
    print(f"Requested ports: {port_a}, {port_b}")
    print(f"Transpiled depth: {compiled.depth()}")
    print(f"Two-qubit gates: {two_qubit_gates}")
    print(f"SWAP gates: {swap_count}")
    print(f"Active circuit qubits: {len(active_qubits)}")
    print("\nTranspiled circuit:")
    print(compiled.draw(output="text"))

    return {
        "architecture": name,
        "ports": f"{port_a},{port_b}",
        "depth": compiled.depth(),
        "two_qubit_gates": two_qubit_gates,
        "swap_gates": swap_count,
        "active_qubits": len(active_qubits),
    }


def main():
    validate_architectures()

    results = []
    for name, config in ARCHITECTURES.items():
        results.append(benchmark_architecture(name, config))

    print("\n=== SUMMARY ===")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
