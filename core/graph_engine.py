import networkx as nx
from pyvis.network import Network
import os


class ChordGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self, genre_data):
        self.graph.clear()

        for source, target, weight in genre_data["edges"]:
            self.graph.add_edge(
                source,
                target,
                weight=weight
            )

    def create_pyvis_network(self):
        net = Network(
            directed=True,
            height="650px",
            width="100%",
            cdn_resources="in_line",
            bgcolor="#ffffff",
            font_color="#222222"
        )

        for node in self.graph.nodes():
            net.add_node(
                node,
                label=str(node),
                size=35,
                font={
                    "size": 24,
                    "face": "Arial",
                    "color": "#222222",
                    "bold": True
                },
                shape="circle"
            )

        for source, target in self.graph.edges():
            net.add_edge(
                source,
                target,
                arrows="to",
                width=2,
                smooth={
                    "enabled": True,
                    "type": "curvedCW",
                    "roundness": 0.25
                }
            )

        net.set_options("""
        {
          "nodes": {
            "borderWidth": 2,
            "shadow": false
          },
          "edges": {
            "color": {
              "color": "#666666",
              "highlight": "#222222"
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.8
              }
            },
            "font": {
              "size": 0
            }
          },
          "physics": {
            "enabled": true,
            "repulsion": {
              "nodeDistance": 220,
              "centralGravity": 0.15,
              "springLength": 180,
              "springStrength": 0.05,
              "damping": 0.09
            },
            "solver": "repulsion",
            "stabilization": {
              "enabled": true,
              "iterations": 300
            }
          }
        }
        """)

        return net

    def to_html(self):
        net = self.create_pyvis_network()
        return net.generate_html(notebook=False)

    def render(self):
        os.makedirs("generated", exist_ok=True)

        net = self.create_pyvis_network()
        html = net.generate_html(notebook=False)

        with open("generated/graph.html", "w", encoding="utf-8") as file:
            file.write(html)