import os
import csv
from datetime import datetime
from fuzzywuzzy import fuzz

def is_duplicate(existing_desc, new_desc):
    similarity = fuzz.ratio(existing_desc, new_desc)
    return similarity > 90  

def get_existing_entries(filename):
    if not os.path.isfile(filename):
        return {}

    existing_entries = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row["Job Title"]
            desc = row["Description"]
            if title in existing_entries:
                existing_entries[title].add(desc)
            else:
                existing_entries[title] = {desc}

    return existing_entries

def get_current_row_count(filename):
    if not os.path.isfile(filename):
        return 0
    with open(filename, mode='r', encoding='utf-8') as file:
        return sum(1 for row in file) - 1  # Subtracting 1 for the header

def save_to_csv(data, filename="results.csv"):
    file_exists = os.path.isfile(filename)
    existing_entries = get_existing_entries(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Modified header to include "Hidden" column
            writer.writerow(["Row Number", "Source", "Timestamp", "Job Title", "Description", "Href", "Hidden"])

        row_number = get_current_row_count(filename)
        for item in data:
            title = item['title']
            desc = item['description']

            # Updated duplicate check
            duplicate = False
            if title in existing_entries:
                for existing_desc in existing_entries[title]:
                    if is_duplicate(existing_desc, desc):
                        duplicate = True
                        break
            if duplicate:
                continue

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_number += 1
            base_url = "https://it.indeed.com" if item['source'] == 'indeed' else ''
            # Added value 0 for "Hidden" column in the writerow function
            writer.writerow([row_number, item['source'], timestamp, title, desc, base_url + item['href'], 0])