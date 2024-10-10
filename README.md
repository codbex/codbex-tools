### Markdown Documentation for GitHub Repository Dependency Checker and Galaxy Dependency Graph

---

## **Script 1: GitHub Repository Dependency Checker**

This script fetches repositories from a specified GitHub organization, locates their `package.json` files, parses dependencies, and checks for deprecated versions. It uses multithreading to optimize the process and outputs various JSON files for further analysis.

### **Requirements:**
- Python 3.x
- `requests` library
- GitHub access token (with read permissions for repositories)
- Install dependencies automatically ```pip install -r req.txt```

### **Files Generated:**
- `nopkgfile.txt`: A list of repositories that don't contain a `package.json` file.
- `reponv.json`: A list of repositories with their names and versions.
- `deprecated.json`: Details about dependencies and whether they are deprecated.
- `dependency_map.json`: A map of each repository and its dependencies, along with their versions.

### **Key Functions:**
- `write_to_file(file_name, data, mode="w")`: Helper function to write data to a file.
- `save_package_json(repo_name, package_content)`: Saves the `package.json` file of a repository in a local directory.
- `get_repositories()`: Fetches all repositories from a GitHub organization using pagination.
- `search_package_json(repo_name, path="")`: Recursively searches for the `package.json` file in a repository.
- `parse_dependencies(repositories_data)`: Extracts and processes dependencies from `package.json` files.
- `check_for_deprecated(all_dependencies)`: Identifies outdated (deprecated) dependencies.
- `create_dependency_map(repositories_data, latest_versions)`: Creates a comprehensive map of repository dependencies and versions.

### **Script Workflow:**
1. **Fetching Repositories**: The script starts by fetching all repositories from the specified GitHub organization using the GitHub API.
2. **Searching for `package.json`**: For each repository, the script searches for a `package.json` file, first in the root and then recursively in subdirectories.
3. **Saving `package.json`**: The script saves the `package.json` file in a local folder for future use.
4. **Dependency Parsing**: It parses the dependencies from each `package.json` and compiles them for analysis.
5. **Deprecated Check**: The script compares the version of each dependency in the repositories against the latest version and flags any outdated versions.
6. **Outputs**: It writes various JSON files to document repositories, their versions, dependencies, and deprecated dependencies.

### **How to Run:**
1. Install the required library: `pip install requests`.
2. Set your GitHub access token in the `ACCESS_TOKEN` constant.
3. Run the script:
    ```bash
    python github_dependency_checker.py
    ```

---

## **Script 2: Galaxy Dependency Graph Generator**

This script generates a "galaxy-like" dependency tree for repositories based on the `package.json` files in a local folder. The tree is visualized using the Graphviz library and saved as an SVG file.

### **Requirements:**
- Python 3.x
- `graphviz` library
- Install dependencies automatically ```pip install -r req.txt```

### **Files Generated:**
- `galaxy_dependency_tree.svg`: An SVG file representing the dependencies as a galaxy-style graph.

### **Key Functions:**
- `load_local_package_json_files()`: Loads all `package.json` files from the local `projects` directory.
- `create_galaxy_dependency_graph(package_data)`: Creates a radial dependency tree using Graphviz, with each repository as a circle and its dependencies as elliptical nodes.
- `save_dependency_graph(graph, svg_filename="galaxy_dependency_tree")`: Renders and saves the dependency graph as an SVG file.

### **Script Workflow:**
1. **Loading Local `package.json` Files**: The script looks into the `projects` folder and loads all the `package.json` files found in the subdirectories (assumed to be named after repositories).
2. **Creating the Dependency Graph**: It creates a radial galaxy-like dependency graph using Graphviz's `neato` engine. Each repository is represented by a circular node, while dependencies are represented by elliptical nodes.
3. **Saving the Graph**: The graph is rendered and saved as an SVG file.

### **How to Run:**
1. Install Graphviz and its Python binding:
    ```bash
    pip install graphviz
    ```
2. Make sure the `projects` folder contains subdirectories named after repositories, each containing a `package.json`.
3. Run the script:
    ```bash
    python galaxy_dependency_graph.py
    ```

---

### Example Output:

The output will be a visual graph saved as an SVG file. Repositories are shown as circular nodes, and their dependencies are linked as ellipses, resulting in a galaxy-like layout that is easy to understand at a glance.

---

![galaxy_dependency_tree](https://github.com/user-attachments/assets/0b199374-914d-45c2-a330-02c82a5509c4)


