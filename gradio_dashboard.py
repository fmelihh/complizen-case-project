import os
import requests
import gradio as gr
import networkx as nx
from typing import Any
import plotly.graph_objs as go


def _build_hover_text(device_info: dict[str, Any]) -> str:
    text = []
    for k, v in device_info.items():
        text.append(f"{k}: {v}")

    return "<br> ".join(text)


def generate_graph_plotly(depth: int, device_k_number: str):
    if not device_k_number:
        raise ValueError("Device number cannot be empty.")

    response = requests.get(
        os.getenv("API_URL", "http://localhost:8000/device-dag"),
        params={"depth": depth, "k_number": device_k_number},
    )
    data = response.json()

    directed_graph = nx.DiGraph()
    directed_graph.add_edges_from(data["dag_list"])

    pos = nx.spring_layout(directed_graph, seed=42)

    node_x, node_y, hover_text = [], [], []
    for node in directed_graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        device_info = data["device_hashmap"][node]
        text = _build_hover_text(
            {
                "Device Name": device_info["device_name"],
                "K Number": device_info["k_number"],
                "State": device_info["state"],
            }
        )

        hover_text.append(text)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[node for node in directed_graph.nodes()],
        hoverinfo="text",
        marker=dict(size=20, color="lightblue", line=dict(width=2)),
        textposition="top center",
        hovertext=hover_text,
    )

    annotations = []
    edge_x, edge_y = [], []
    for edge in directed_graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        annotations.append(
            dict(
                ax=x0,
                ay=y0,
                x=x1,
                y=y1,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=1,
                opacity=0.8,
            )
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=f"Directed Graph (Device K Number: {device_k_number}, Depth: {depth})",
            font_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=annotations,
        ),
    )

    return fig


with gr.Blocks(title="Interactive Predicate Device Directed Graph Visualizer") as demo:
    gr.Markdown("## Predicate Devices Graph Visualizer")
    gr.Markdown("Input k-number and depth to generate a directed graph.")

    graph_output = gr.Plot(label="Directed Graph")

    with gr.Row():
        depth_input = gr.Number(label="Node Depth", value=3)
        k_number_input = gr.Text(label="Device K Number")

    submit_btn = gr.Button("Generate Graph")

    submit_btn.click(
        fn=generate_graph_plotly,
        inputs=[depth_input, k_number_input],
        outputs=graph_output,
    )

if __name__ == "__main__":
    demo.launch()
