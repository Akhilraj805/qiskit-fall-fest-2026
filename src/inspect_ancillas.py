
import sys
from pathlib import Path
from collections import deque

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "qff_basic_benchmark"))

from qff_basic_benchmark import load_all_models


def distances_from(source, edges, num_qubits):
    graph = {q: [] for q in range(num_qubits)}

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    distances = {source: 0}
    queue = deque([source])

    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances, graph


def main():
    models = load_all_models()

    for name, model in models.items():
        port_a, port_b = model.ports
        dist_a, graph = distances_from(
            port_a, model.edges, model.num_qubits
        )
        dist_b, _ = distances_from(
            port_b, model.edges, model.num_qubits
        )

        candidates = [
            (
                dist_a[q] + dist_b[q],
                max(dist_a[q], dist_b[q]),
                q,
                dist_a[q],
                dist_b[q],
                graph[q],
            )
            for q in range(model.num_qubits)
            if q not in model.ports
        ]
        candidates.sort()

        print(f"\n{'=' * 60}")
        print(f"MODEL: {name}")
        print(f"Ports: A={port_a}, B={port_b}")
        print("Ancilla candidates (best graph proximity first):")
        print("qubit | distance A | distance B | neighbors")

        for total, worst, q, da, db, neighbors in candidates[:10]:
            print(
                f"{q:5} | {da:10} | {db:10} | {neighbors}"
            )


if __name__ == "__main__":
    main()
