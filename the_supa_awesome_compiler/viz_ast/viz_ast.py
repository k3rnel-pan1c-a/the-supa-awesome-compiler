import json
from graphviz import Digraph


class ASTVisualizer:
    def __init__(self):
        self.graph = Digraph("AST", format="png")
        self.node_count = 0

    def generate_node_id(self):
        self.node_count += 1
        return f"node{self.node_count}"

    def add_node(self, label):
        node_id = self.generate_node_id()
        self.graph.node(node_id, label)
        return node_id

    def draw_ast(self, json_node):
        if isinstance(json_node, dict):
            node_label = json_node.get("type", "Unknown")
            node_id = self.add_node(node_label)

            for key, value in json_node.items():
                if key != "type":
                    child_node_id = self.draw_ast(value)
                    if isinstance(child_node_id, list):  # For lists of children
                        for child_id in child_node_id:
                            self.graph.edge(node_id, child_id, label=key)
                    else:
                        self.graph.edge(node_id, child_node_id, label=key)
            return node_id

        elif isinstance(json_node, list):
            child_ids = []
            for item in json_node:
                child_ids.append(self.draw_ast(item))
            return child_ids

        else:  # For literals or primitives
            return self.add_node(str(json_node))

    def render(self, filename="ast"):
        self.graph.render(filename, view=True)


with open("../debug/ast.json") as f:
    ast_json = json.load(f)

visualizer = ASTVisualizer()
visualizer.draw_ast(ast_json)
visualizer.render("AST")
