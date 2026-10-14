
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a simple two-qubit quantum circuit
qc = QuantumCircuit(2, 2)

# Prepare a Bell state
qc.h(0)
qc.cx(0, 1)

# Measure both qubits
qc.measure([0, 1], [0, 1])

# Run the circuit on a simulator
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()

print("Circuit:")
print(qc.draw())

print("\nMeasurement results:")
print(result.get_counts())
