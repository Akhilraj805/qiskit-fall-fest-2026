
from pathlib import Path
import sys

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "qff_basic_benchmark"))

from qff_basic_benchmark import load_all_models, SHOTS

models = load_all_models(noise="common")

print("Qiskit Fall Fest — Common Noise Diagnostic")
print("=" * 50)

for name, model in models.items():
    print(f"\nMODEL: {name}")
    print("Qubits:", model.num_qubits)
    print("Ports:", model.ports)
    print("Number of graph edges:", len(model.edges))
    print("Gate set:", model.basis_gates)
    print("Noise rates:", model.error_rates)
    print("Port distance:", model.port_distance())

    # Prepare a Bell state on the two logical qubits.
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    compiled = transpile(
        qc,
        backend=model.backend,
        initial_layout=list(model.ports),
        seed_transpiler=42,
        optimization_level=1,
    )

    
    print("Compiled two-qubit physical edges:")

    layout = compiled.layout
    for instruction in compiled.data:
        if instruction.operation.name == "cz":
            q0 = compiled.find_bit(instruction.qubits[0]).index
            q1 = compiled.find_bit(instruction.qubits[1]).index

            physical_q0 = layout.initial_layout[q0]
            physical_q1 = layout.initial_layout[q1]

            print(f"  {physical_q0} -- {physical_q1}")


    print("Compiled operations:", dict(compiled.count_ops()))
    print("Compiled depth:", compiled.depth())
    print("Compiled width:", compiled.num_qubits)
    print("Compiled circuit:")
    print(compiled.draw(output="text", fold=100))

    print("Running noisy simulator...")
    counts = model.backend.run(
        compiled, shots=SHOTS, seed_simulator=12345
    ).result().get_counts()

    print("Measurement counts:", counts)
