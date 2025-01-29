#!/bin/bash
set -x

# print the current working directory
echo "Current working directory: $(pwd)"

# verify whether the image file exists
if [ -f "$2" ]; then
 echo "Image: $2"
fi

# Get the directory of the current markdown file
md_file_dir=$(dirname "$1")

# Get the current markdown file name without extension
current_md_file=$(basename "$1" .md)

# Extract the content after the last hyphen
suffix=$(echo "$current_md_file" | awk -F'-' '{print $NF}')

# Define the target directory
target_dir="assets/img/$suffix"

# Create the directory if it doesn't exist
mkdir -p "$target_dir"

# Move the image file to the target directory
mv "$2" "$target_dir"

# List the contents of the target directory
ls -la "$target_dir"