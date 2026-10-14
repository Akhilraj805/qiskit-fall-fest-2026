
"""
Illustrative processor topologies for the Qiskit Fall Fest benchmark.

IMPORTANT:
These are experimental assumptions, not official organizer-supplied
processor graphs, port assignments, or hardware specifications.
"""

ARCHITECTURES = {
    "2016_inspired": {
        "num_qubits": 5,
        "edges": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
        ],
        "ports": (0, 4),
        "description": "Linear connectivity; distant ports require routing.",
    },

    "contemporary_ibm_style": {
        "num_qubits": 7,
        "edges": [
            (0, 1),
            (1, 2),
            (2, 3),
            (1, 4),
            (4, 5),
            (2, 6),
            (6, 5),
        ],
        "ports": (0, 3),
        "description": "Illustrative sparse, branched connectivity.",
    },

    "hyperbolic_inspired": {
        "num_qubits": 7,
        "edges": [
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 4),
            (1, 5),
            (2, 6),
        ],
        "ports": (4, 6),
        "description": "Illustrative tree-like connectivity.",
    },
}


def validate_architectures():
    for name, config in ARCHITECTURES.items():
        n = config["num_qubits"]
        a, b = config["ports"]

        assert a != b, f"{name}: ports must be different"
        assert 0 <= a < n and 0 <= b < n, (
            f"{name}: port outside the graph"
        )

        for u, v in config["edges"]:
            assert 0 <= u < n and 0 <= v < n
            assert u != v

        print(
            f"{name}: {n} qubits, "
            f"{len(config['edges'])} couplings, ports={config['ports']}"
        )


if __name__ == "__main__":
    validate_architectures()
