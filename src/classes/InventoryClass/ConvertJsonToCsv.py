import glob
import os
import json

# Directory containing the JSON files
directory = 'public/GeneratedInventories/'

# List all.json files in the directory, sort them by modification time, and select the latest
latest_json_file = sorted(glob.glob(os.path.join(directory, '*.json')), key=os.path.getmtime)[-1]

# Load the JSON data from the latest file
with open(latest_json_file, 'r') as f:
    inventory_data = json.load(f)

# Now, proceed with converting the JSON data to CSV as previously described
import csv

# Define the field names for the CSV file
fields = ["Language", "Category", "Name", "JW ID", "Edition", "Quantity"]

# Create a CSV writer
json_file_without_extension = latest_json_file.strip('.json')
inventory_csv = json_file_without_extension + '.csv'
with open(inventory_csv, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row
    writer.writerow(fields)
    # Write the data rows
    for item in inventory_data:
        writer.writerow([item[field] for field in fields])
