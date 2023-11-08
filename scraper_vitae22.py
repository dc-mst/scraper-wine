import csv
import re

user_input = input("Enter the string to replace [x]: ")

def is_wine_info(line):
    return line.strip().startswith(("Bianco", "Rosso", "Rosato"))

def is_winery_end(line):
    return line.strip() == "WINERYEND"

with open(f'static/pdf/vitae22-{user_input}.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

wine_data = []
winery = ''
current_winery = ''
current_name = ""
current_review = ""
current_pairing = ""
current_price = ""
current_aging = ""
current_alcohol = ""
current_bottles = "" 
current_grapes = ""  # Initialize variable for grapes
current_scoreAIS = "" 

for i in range(len(lines) - 1):
    line = lines[i].strip()
    next_line = lines[i + 1].strip()





    
    
    # print(f"Processing line {i}: {line}") 
    if is_winery_end(line):
            winery = lines[i + 1].strip() if i + 1 < len(lines) else ''
            print(f"{winery}")

    if line == line.upper() and line and not is_winery_end(line):
        if current_name:
            current_name += " " + line
        else:
            current_name = line
            current_winery = winery if winery else lines[0].strip()

    if reading_review and not is_wine_info(line) and not line == line.upper():
        current_review += " " + line.strip()

    price_match = re.search(r'€\s*(\d+[\.,]?\d*)', line)
    if price_match:
        current_price = price_match.group(1).replace(',', '.')

    mat_match = re.search(r'Mat\.\s*(.*)', line)
    if mat_match:
        current_aging = mat_match.group(1)
        reading_review = True
        current_review = ""

    alc_match = re.search(r'Alc\.\s*(.*?)\s*(?:\||$)', line)
    if alc_match:
        current_alcohol = alc_match.group(1)

    bt_match = re.search(r'Bt\.\s*(.*?)\s*(?:\||$)', line)  # Search for bottle count
    if bt_match:
        current_bottles_raw = bt_match.group(1)
        try:
            current_bottles_number = int(current_bottles_raw.replace(',', '').replace('.', ''))
            if current_bottles_number >= 1000:
                current_bottles = str(current_bottles_number // 1000)  # Keep only the thousands
            else:
                current_bottles = str(current_bottles_number)
        except ValueError:
            current_bottles = current_bottles_raw  

    if is_wine_info(line):
        grapes_match = re.search(r'- (.*?)\s*\|', line)
        if grapes_match:
            current_grapes = grapes_match.group(1).replace(", ", " – ")

    if current_name and (is_wine_info(next_line) or is_winery_end(next_line)):
        vintage_match = re.search(r'\b\d{4}\b', current_name)
        if vintage_match:
            vintage = vintage_match.group(0)
            current_name = current_name.replace(vintage, '').strip()
        else:
            vintage = '2022'

         # Check if the wine name starts with "(**)"
        scoreAIS_match = re.search(r'\((.*?)\)', current_name)
        if scoreAIS_match:
            # Extract content within parentheses and assign it to scoreAIS
            current_scoreAIS = scoreAIS_match.group(1)

            # Remove the matched string and everything before it from the wine name
            current_name = current_name.split(f'({current_scoreAIS})', 1)[1].strip()

        # Remove "(**)" and its content from the wine name
        current_name = current_name.replace(f"(**){current_scoreAIS}", '').strip()
        
        if len(current_review) < 70 and "abbinamento" in current_review.lower():
            current_pairing = current_review.replace("abbinamento", "").strip()
            current_review = ""
        else:
            periods = [m.start() for m in re.finditer(r'\.', current_review)]
            if len(periods) > 1:
                penultimate_period = periods[-2]
                current_pairing = current_review[penultimate_period+1:].strip()
                current_review = current_review[:penultimate_period+1].strip()
        
        wine_data.append([current_name.title(), current_winery, vintage, current_review.replace("- ", "").strip(), current_pairing.strip(), current_price.strip(), current_aging.strip(), current_alcohol.strip(), current_bottles.strip(), current_grapes.strip(), current_scoreAIS.strip()])
        current_name = ""
        current_winery = ""
        current_review = ""
        current_pairing = ""
        current_price = ""
        current_aging = ""
        current_alcohol = ""
        current_bottles = ""
        current_grapes = ""  # Reset grapes for next entry
        current_scoreAIS = ""
        reading_review = False

columns = ['Entry', 'Ref', 'OLDRS', 'RANK', 'RS', 'RAWQP', 'QPRANK', 'QP', 'RANK2', 'RS2', 'RAWQP2', 'QP2', 
               'RANK3', 'RS3', 'RAWQP3', 'QP3', 'RawAvg', 'RatingYear', 'Vintage', 'Qterms', 'FullName', 
               'AppellationLevel', 'AppellationName', 'WineryName', 'Region', 'EvaluationAvg', 'Price', 'Grapes', 
               'Pairing', 'ScoreAvg', 'EvaluationAIS', 'ScoreAIS', 'EvaluationGR', 'ScoreGR', 'SLC', 'TLC', 
               'WineTypeIT', 'WineType', 'Alcohol', 'Bottles', 'AgingMonths', 'AgingTypeIT', 'AgingType', 'Notes',
               'Tasting Notes', 'Country', 'VintageNV', 'Method', 'Sweetness']

with open(f'static/pdf/vitae22-{user_input}.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(columns)
    for name, winery, vintage, review, pairing, price, aging, alcohol, bottles, grapes, scoreAIS in wine_data:
        row = [''] * len(columns)
        row[columns.index('FullName')] = name
        row[columns.index('WineryName')] = winery.title()
        row[columns.index('Vintage')] = vintage
        row[columns.index('Tasting Notes')] = review
        row[columns.index('Pairing')] = pairing
        row[columns.index('Price')] = price
        row[columns.index('AgingMonths')] = aging
        row[columns.index('Alcohol')] = alcohol
        row[columns.index('Bottles')] = bottles
        row[columns.index('Grapes')] = grapes
        row[columns.index('ScoreAIS')] = scoreAIS
        # Hardcoded content
        row[columns.index('RatingYear')] = '2022'
        row[columns.index('Entry')] = '2'
        row[columns.index('Region')] = user_input.title()
        row[columns.index('Country')] = 'Italy'
        row[columns.index('EvaluationGR')] = 'nd'
        row[columns.index('ScoreGR')] = 'nd'

        csvwriter.writerow(row)

print("Wine names, vintages, tasting notes, pairings, prices, alcohol contents, bottle counts, and grape varieties have been extracted to vitae22-vda.csv")
