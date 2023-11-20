import re
import csv

# Function to check if a line contains a wine name
def is_wine_name(line):
    return bool(re.match(r'^[A-Z0-9\(\) ]+$', line))

# Function to extract the score and clean the wine name
def extract_score_and_clean_name(wine_name):
    match = re.search(r'\((\d+)\)', wine_name)
    if match:
        score = match.group(1)  # Extract the score
        cleaned_name = re.sub(r'\(\d+\)', '', wine_name).strip().title()  # Remove the score from the name
        return cleaned_name, score
    return wine_name.title(), ''  # Return the original name and empty score if no match

# Function to extract grape varieties
def extract_grapes(line):
    match = re.search(r' - (.*?) \|', line)
    if match:
        grapes = match.group(1).replace(', ', ' – ')
        return grapes
    return ''

# Function to extract price
def extract_price(line):
    match = re.search(r'€(.*?) ', line)
    if match:
        price = match.group(1)
        return price
    return ''

# Function to extract Alcohol
def extract_alcohol(line):
    match = re.search(r'Alc.(.*?)%', line)
    if match:
        alcohol = match.group(1)
        return alcohol
    return ''

# Function to extract Aging
def extract_aging(line):
    match = re.search(r'Mat. (.*?)\n', line)
    if match:
        aging = match.group(1)
        return aging
    return ''

# Function to extract bottles
def extract_bottles(line):
    match = re.search(r'Bt.(.*?) ', line)
    if match:
        bottles = match.group(1).replace('.', '')
        if len(bottles) > 3:  # Check if the length is more than three characters
            bottles = bottles[:-3]  # Remove the last three characters
        return bottles
    return ''

# Function to process tasting notes and extract pairing
def process_tasting_notes(tasting_notes):
    # Check if 'tasting_notes' starts with 'abbinamento'
    if tasting_notes.lower().startswith('abbinamento'):
        pairing = tasting_notes.replace('abbinamento ', '', 1).rstrip('. ')
        tasting_notes = ''
    else:
        # Split the notes into sentences
        sentences = tasting_notes.split('. ')
        if len(sentences) > 1:
            # Check if the last sentence is short, likely a pairing suggestion
            if len(sentences[-1]) < 50:  # Assuming pairing suggestions are shorter
                pairing = sentences[-1].rstrip('. ')
                tasting_notes = ' '.join(sentences[:-1])
            else:
                # Extract the part between the last and penultimate period
                pairing = sentences[-2].rstrip('. ')
                tasting_notes = ' '.join(sentences[:-2])
        else:
            pairing = ''
    return tasting_notes, pairing

# Your text file containing the wine list
file_path = 'static/pdf/vitae22-piemonte.txt'
winery_name = ''
wines = []

# Read the file and process the text
with open(file_path, 'r') as file:
    lines = file.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == 'WINERYEND':  # Check for the winery name end delimiter
        winery_name = lines[i + 1].strip().title()  # Read the next line as winery name
        i += 1  # Skip the winery name line
    elif is_wine_name(line):  # Check for wine names
        cleaned_name, score = extract_score_and_clean_name(line)
        grapes = extract_grapes(lines[i + 1]) if (i + 1) < len(lines) else '' # Extract grapes
        price = extract_price(lines[i + 1]) if (i + 1) < len(lines) else ''
        bottles = extract_bottles(lines[i + 1]) if (i + 1) < len(lines) else ''
        alcohol = extract_alcohol(lines[i + 1]) if (i + 1) < len(lines) else ''
        aging = extract_aging(lines[i + 1]) if (i + 1) < len(lines) else ''
        # Assuming the third line after the wine name contains the tasting notes
        original_tasting_notes = lines[i + 2].strip() if (i + 2) < len(lines) else ''
        tasting_notes, pairing = process_tasting_notes(original_tasting_notes)
        wines.append((winery_name, cleaned_name, score, grapes, tasting_notes, pairing, price, bottles, alcohol, aging))
        i += 2  # Skip the next two lines (expecting them not to be wine names)
    i += 1  # Move to the next line

# Now, we will write the extracted information to a CSV file
with open('static/pdf/vitae22-piemonte.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Writing the header of the CSV
    writer.writerow(['FullName', 'Winery', 'ScoreAIS', 'Grapes', 'Tasting Notes', 'Pairing', 'Price', 'Bottles', 'Alcohol', 'Aging'])
    # Writing the wine data
    for wine in wines:
        writer.writerow(wine)
