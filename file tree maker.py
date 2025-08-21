import os


def generate_file_tree(dir_path, prefix=""):
    files = [f for f in os.listdir(dir_path) if not f.startswith(".")]
    files.sort()
    for idx, name in enumerate(files):
        path = os.path.join(dir_path, name)
        connector = "└── " if idx == len(files) - 1 else "├── "
        print(prefix + connector + name)
        if os.path.isdir(path):
            extension = "    " if idx == len(files) - 1 else "│   "
            generate_file_tree(path, prefix + extension)


print("project-root/")
generate_file_tree(".")
