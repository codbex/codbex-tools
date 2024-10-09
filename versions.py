import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants for GitHub API
GITHUB_API_URL = "https://api.github.com"
ORGANIZATION = "codbex"
ACCESS_TOKEN = ""  # Add your GitHub token here
HEADERS = {
    "Authorization": f"token {ACCESS_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Output files
NO_PKG_FILE = "nopkgfile.txt"
REPO_NV_FILE = "reponv.json"
DEPRECATED_FILE = "deprecated.json"
DEPENDENCY_MAP_FILE = "dependency_map.json"
PROJECT_FOLDER = "projects"  # Folder to save package.json files

def write_to_file(file_name, data, mode="w"):
    """Helper function to write data to a file."""
    print(f"Writing data to file: {file_name}")
    with open(file_name, mode) as file:
        file.write(data)
    print(f"Data successfully written to {file_name}")

def save_package_json(repo_name, package_content):
    """Save the package.json content to a folder named after the repository."""
    repo_dir = os.path.join(PROJECT_FOLDER, repo_name)
    os.makedirs(repo_dir, exist_ok=True)  # Create the folder if it doesn't exist
    
    package_json_path = os.path.join(repo_dir, "package.json")
    with open(package_json_path, 'w') as f:
        json.dump(package_content, f, indent=4)
    print(f"Saved package.json for {repo_name} at {package_json_path}")

def get_repositories():
    """Fetch all repositories from the organization with pagination."""
    print(f"Fetching repositories from organization: {ORGANIZATION}")
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/orgs/{ORGANIZATION}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            repos_page = response.json()
            repos.extend(repos_page)
            if len(repos_page) < 100:  # Stop when we receive fewer than 100 repos
                break
            page += 1
        else:
            print(f"Error fetching repositories: {response.status_code}")
            return []  # Return empty list to indicate failure
    print(f"Total repositories fetched: {len(repos)}")
    return repos

def search_package_json(repo_name, path=""):
    """Recursively search for package.json in a repository."""
    if path:
        print(f"Searching in {repo_name}/{path}...")
    else:
        print(f"Searching in root directory of {repo_name}...")

    url = f"{GITHUB_API_URL}/repos/{ORGANIZATION}/{repo_name}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            print(f"Inspecting {item['name']} ({item['type']}) in {repo_name}/{path}...")

            if item['type'] == 'file' and item['name'] == 'package.json':
                print(f"Found package.json in {repo_name} at {item['path']}")
                return item  # Return the package.json file metadata

            elif item['type'] == 'dir':  # If it's a directory, search within it recursively
                sub_package_json = search_package_json(repo_name, item['path'])
                if sub_package_json:
                    return sub_package_json
    else:
        print(f"Error: Failed to fetch contents from {repo_name}/{path}. Status code: {response.status_code}")

    print(f"No package.json found in {repo_name}/{path}...")
    return None

def parse_dependencies(repositories_data):
    """Parse dependencies from all repos to check for deprecated versions."""
    print("Parsing dependencies from repositories...")
    all_dependencies = {}
    repo_dependencies = {}

    for repo_name, pkg_data in repositories_data.items():
        dependencies = pkg_data.get("dependencies", {})
        repo_dependencies[repo_name] = dependencies

        for dep, version in dependencies.items():
            if dep not in all_dependencies:
                all_dependencies[dep] = []
            all_dependencies[dep].append({"repo": repo_name, "version": version})

    print("Dependencies parsed successfully.")
    return all_dependencies, repo_dependencies

def check_for_deprecated(all_dependencies):
    """Compare dependency versions and identify deprecated ones."""
    print("Checking for deprecated dependencies...")
    deprecated_info = {}

    for dep, versions in all_dependencies.items():
        sorted_versions = sorted(versions, key=lambda x: x['version'], reverse=True)
        latest_version = sorted_versions[0]["version"]

        deprecated_info[dep] = {
            "latest_version": latest_version,
            "repos_with_deprecated": []
        }

        for version_info in sorted_versions[1:]:  # Compare with the latest version
            if version_info["version"] != latest_version:
                deprecated_info[dep]["repos_with_deprecated"].append({
                    "repo": version_info["repo"],
                    "actual_version": version_info["version"],
                    "latest_version": latest_version
                })

    print("Deprecated dependencies check complete.")
    return deprecated_info

def create_dependency_map(repositories_data, latest_versions):
    """Create a dependency map for all repositories."""
    print("Creating dependency map...")
    dependency_map = {}

    for repo_name, pkg_data in repositories_data.items():
        dependencies = pkg_data.get("dependencies", {})
        dependency_map[repo_name] = {
            "actual_version": pkg_data.get("version", "unknown"),
            "dependencies": {}
        }
        for dep, version in dependencies.items():
            dependency_map[repo_name]["dependencies"][dep] = {
                "actual_version": version,
                "latest_version": latest_versions.get(dep, "unknown")
            }

    print("Dependency map created successfully.")
    return dependency_map

def main():
    print("Starting process...")
    
    # Create a folder for saving package.json files
    os.makedirs(PROJECT_FOLDER, exist_ok=True)

    repositories = get_repositories()
    if not repositories:  # If fetching repos failed, exit early
        return

    no_package_repos = []
    repo_nv_data = {}
    repositories_data = {}

    # Using ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_repo = {executor.submit(search_package_json, repo['name']): repo for repo in repositories}

        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                package_json = future.result()
                if package_json:
                    print(f"Fetching content of package.json from {repo['name']}.")
                    package_content = requests.get(package_json['download_url']).json()
                    
                    # Save package.json content to a folder named after the repo
                    save_package_json(repo['name'], package_content)

                    # Store repo name and version
                    repo_nv_data[repo['name']] = {
                        "name": package_content.get("name", repo['name']),
                        "version": package_content.get("version", "unknown")
                    }
                    repositories_data[repo['name']] = package_content  # Store data for dependency comparison
                else:
                    no_package_repos.append(repo['name'])
            except Exception as e:
                print(f"Error processing {repo['name']}: {e}")

    # Write repositories without package.json to nopkgfile.txt
    if no_package_repos:
        print(f"Repositories without package.json: {no_package_repos}")
        write_to_file(NO_PKG_FILE, "\n".join(no_package_repos) + "\n")

    # Write repo name and version to reponv.json
    if repo_nv_data:
        print(f"Writing repository name and version to {REPO_NV_FILE}.")
        write_to_file(REPO_NV_FILE, json.dumps(repo_nv_data, indent=4))

    # Parse dependencies to check for deprecated versions
    all_dependencies, repo_dependencies = parse_dependencies(repositories_data)
    deprecated_info = check_for_deprecated(all_dependencies)

    # Write deprecated dependencies to deprecated.json
    if deprecated_info:
        print(f"Writing deprecated dependencies information to {DEPRECATED_FILE}.")
        write_to_file(DEPRECATED_FILE, json.dumps(deprecated_info, indent=4))

    # Create and write the dependency map to a file
    dependency_map = create_dependency_map(repositories_data, repo_nv_data)
    print(f"Writing dependency map to {DEPENDENCY_MAP_FILE}.")
    write_to_file(DEPENDENCY_MAP_FILE, json.dumps(dependency_map, indent=4))

    print("Process complete!")

if __name__ == "__main__":
    main()
