import os

def print_tree(startpath, prefix=""):
    # Folders to skip to keep the output clean
    ignore_dirs = {
        '.git', '.idea', '__pycache__', 'venv', 'env', 
        '.dart_tool', 'build', '.gradle'
    }

    # Get all items in directory and sort them (folders first, then files)
    try:
        items = os.listdir(startpath)
    except PermissionError:
        return # Skip folders we can't access

    items.sort(key=lambda x: (not os.path.isdir(os.path.join(startpath, x)), x.lower()))

    total_items = len(items)
    
    for index, item in enumerate(items):
        if item in ignore_dirs:
            continue
            
        path = os.path.join(startpath, item)
        is_last = (index == total_items - 1)
        
        # Visual markers for the tree
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{item}")

        if os.path.isdir(path):
            # Recursively print sub-directories
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)

if __name__ == "__main__":
    # "." means the current directory. Change this path if the script is elsewhere.
    print(f"Project Structure: {os.path.abspath('.')}")
    print_tree(".")