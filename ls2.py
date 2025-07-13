"""
    @author RazrCraft
    @create date 2025-06-19 01:49:37
    @modify date 2025-06-19 02:35:21
    @desc Since Minescript's built-in ls command no longer lists script commands, I made this simple script to list them.
          First, it reads the config.txt file and extracts all valid paths from the command_path setting, then lists (name only) 
          all .py files found in those paths. If command_path isn't found in the file, Minescript's default paths are 
          used (minescript directory and system/exec within it).
 """
import os
import sys
import re

# Path to config.txt
config_path = "./minescript/config.txt"
command_path_value = None

# Read config.txt and extract command_path
with open(config_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        match = re.match(r'command_path\s*=\s*"(.*?)"', line)
        if match:
            command_path_value = match.group(1)
            break

if not command_path_value:
    # Use defaults
    command_path_value = ".\\;system\\exec"

# Split paths by semicolon
paths = [p.strip() for p in command_path_value.split(";") if p.strip()]

# List all .py files in each path
all_py_files = []
for rel_path in paths:
    abs_path = os.path.join(os.path.dirname(config_path), rel_path)
    if os.path.isdir(abs_path):
        for fname in os.listdir(abs_path):
            if fname.endswith(".py"):
                all_py_files.append(os.path.join(abs_path, fname))

print("Minescript script commands:", file=sys.stderr)
for py_file in all_py_files:
    print(f"  {os.path.splitext(os.path.basename(py_file))[0]}", file=sys.stderr)
