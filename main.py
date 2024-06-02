import os
import json
import random
import uuid
import requests

# Step 1: Define the folder containing the JSON files
folder_path = r'C:\Users\Parth\Downloads\Objects'  # Using a raw string

# Step 2: Initialize an empty list to hold all objects and sets for brands and categories
combined_array = []
brands = set()
categories = set()


# Function to check if a photo URL is working
def is_url_working(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


# Step 3: Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):  # Check if the file is a JSON file
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # Load JSON data from the file
            if isinstance(data, list):  # Ensure the data is a list of objects
                for obj in data:
                    if 'brand' in obj:
                        brands.add(obj['brand'])
                    if 'category' in obj:
                        categories.add(obj['category'])


# Format brands and categories as required
def format_entry(name):
    return {
        "value": name,
        "label": name,
        "checked": False,
        "id": str(uuid.uuid4())[:4]  # Generate a short unique ID
    }


formatted_brands = [format_entry(brand) for brand in brands]
formatted_categories = [format_entry(category) for category in categories]

# Combine formatted brands and categories into a new array
formatted_entries = formatted_brands + formatted_categories

# Save formatted entries to a new JSON file
formatted_output_path = os.path.join(folder_path, 'formatted_entries.json')
with open(formatted_output_path, 'w', encoding='utf-8') as formatted_output_file:
    json.dump(formatted_entries, formatted_output_file, indent=4)

print(f'Formatted entries saved to {formatted_output_path}')
