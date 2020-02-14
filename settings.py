import os

# Get the current working directory
base_dir = os.path.dirname(os.path.realpath(__file__))

# Where can we find our source files?
source_folder = os.path.join(base_dir, 'data')
pdf_files = os.listdir(source_folder)
pdf_file_pattern = '*.pdf'

# Where are we putting the output files?
output_folder = os.path.join(base_dir, 'output')
json_files = os.listdir(output_folder)
json_file_pattern = '*.json'

# Make sure the output folder actually exists
if not os.path.isdir(output_folder):
    os.mkdir(output_folder)
