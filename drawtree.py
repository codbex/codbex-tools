import os
import json
from graphviz import Graph

# Constants
PROJECT_FOLDER = "projects"  # Folder where the package.json files are saved

def load_local_package_json_files():
    """Load all package.json files from local directories."""
    package_files = {}
    for repo_dir in os.listdir(PROJECT_FOLDER):
        package_json_path = os.path.join(PROJECT_FOLDER, repo_dir, "package.json")
        if os.path.isfile(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            package_files[repo_dir] = package_data
    return package_files

def create_galaxy_dependency_graph(package_data):
    """Create a galaxy-like dependency tree using Graphviz with a radial layout."""
    dot = Graph(comment='Galaxy Dependency Tree', engine='neato', graph_attr={'overlap': 'scale', 'splines': 'true'})

    for repo_name, pkg_data in package_data.items():
        repo_version = pkg_data.get("version", "unknown")
        repo_label = f"{repo_name} ({repo_version})"
        
        # Add the repository as a node with galaxy-like styling
        dot.node(repo_name, label=repo_label, shape='circle', style='filled', fillcolor='#ffcc00')

        # Get dependencies from package.json
        dependencies = pkg_data.get("dependencies", {})

        for dep_name, dep_version in dependencies.items():
            dep_label = f"{dep_name} ({dep_version})"
            # Add dependency as a node with elliptical shapes for galaxy-like look
            dot.node(dep_name, label=dep_label, shape='ellipse', style='filled', fillcolor='#99ccff')
            # Create edges from the repository to the dependency
            dot.edge(repo_name, dep_name)

    return dot

def save_dependency_graph(graph, svg_filename="galaxy_dependency_tree"):
    """Render and save the dependency graph as an SVG directly."""
    # Set a larger size if needed for the SVG
    graph.attr(size="20,20!")
    graph.render(svg_filename, format="svg")  # Directly render the SVG
    print(f"Galaxy-style dependency graph saved as {svg_filename}.svg")

def main():
    # Step 1: Load all local package.json files
    print("Loading local package.json files...")
    package_data = load_local_package_json_files()

    # Step 2: Create galaxy-like dependency graph
    print("Creating galaxy-style dependency graph...")
    graph = create_galaxy_dependency_graph(package_data)

    # Step 3: Save dependency graph as an SVG
    print("Saving galaxy-style dependency graph as an SVG...")
    save_dependency_graph(graph, "galaxy_dependency_tree")

if __name__ == "__main__":
    main()
