
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rustworkx as rx
from rustworkx.visualization import mpl_draw

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "qff_basic_benchmark"))

from qff_basic_benchmark import load_all_models

OUTPUT_DIR = PROJECT_ROOT / "results" / "architecture_diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PORT_A = "#2ca02c"
PORT_B = "#7b3fe4"
OTHER = "#9db4d8"

models = load_all_models()

for name, model in models.items():
    graph = rx.PyGraph()
    graph.add_nodes_from(range(model.num_qubits))
    graph.add_edges_from_no_data(list(model.edges))

    colors = [OTHER] * model.num_qubits
    colors[model.ports[0]] = PORT_A
    colors[model.ports[1]] = PORT_B

    fig, ax = plt.subplots(figsize=(12, 10))

    positions = model.positions
    if positions is None:
        # Force-directed layout for the contemporary graph.
        positions = rx.spring_layout(graph, seed=42)

    mpl_draw(
        graph,
        pos=positions,
        ax=ax,
        with_labels=True,
        labels=str,
        node_color=colors,
        node_size=100 if model.num_qubits > 50 else 350,
        font_size=5 if model.num_qubits > 50 else 8,
        edge_color="#5a6b8c",
    )

    ax.set_title(
        f"{name.title()} processor: {model.num_qubits} qubits\n"
        f"Port A: {model.ports[0]} (green), "
        f"Port B: {model.ports[1]} (purple)"
    )
    ax.axis("off")

    output = OUTPUT_DIR / f"{name}_architecture.png"
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {output}")

print("\nOfficial model graph diagrams generated.")
