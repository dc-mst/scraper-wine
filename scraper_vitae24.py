import re
import csv
import sys

wine_name_prefixes = sorted(['a', 'aa', 'aaa', 'aaa a', 'aaaa'], key=len, reverse=True)
scoreAIS_mapping = {
    'a': '77',
    'aa': '82',
    'aaa': '86',
    'aaa a': '89',
    'aaaa': '91'
}

def extract_winery_and_wine_names(content):
    winery_blocks = content.split("WINERYEND")
    entries = []

    for block in winery_blocks:
        winery_name = None
        start_index = block.find("wineryname")
        if start_index != -1:
            winery_name = block[start_index + len("wineryname"):].strip().split("\n")[0]

        pattern = r'(' + '|'.join(re.escape(prefix) for prefix in wine_name_prefixes) + r')\s*\n([A-ZÀ-Ÿ\s’\d_]+)\s*(\d{4})'
        matches = list(re.finditer(pattern, block))
        
        for i, match in enumerate(matches):
            prefix_matched = match.group(1)
            wine_name = match.group(2).strip().replace('\n', ' ').title()
            vintage = match.group(3)

            if i < len(matches) - 1:
                # Search for a price between this match and the next
                price_search_area = block[match.end():matches[i+1].start()]
            else:
                # Search for a price after this match
                price_search_area = block[match.end():]

            price_match = re.search(r'€\s?(\d+(\.\d{1,2})?)', price_search_area)
            price = price_match.group(1) if price_match else None

            # Extract grape composition
            grape_start_index = block.find("-", match.end()) + 1
            grape_end_index = block.find("\n", grape_start_index)
            grapes = block[grape_start_index:grape_end_index].strip().replace(",", " –")

            # Extract alcohol content
            alcohol_match = re.search(r'Alc\. (\d+(\.\d+)?)%', block)
            alcohol_content = alcohol_match.group(1) if alcohol_match else None
            
            # Extract additional text
            euro_pos = block.find("| €", match.end())
            if euro_pos != -1:
                newline_after_euro = block.find('\n', euro_pos)
                start_pos = newline_after_euro + 1
            else:
                start_pos = match.end()


            if i < len(matches) - 1:  # If not the last wine
                next_match_start = matches[i+1].start()
                extracted_text = block[start_pos:next_match_start].strip()
            else:  # If the last wine
                extracted_text = block[start_pos:].strip()
                if i < len(matches) - 1:  # If not the last wine
                    next_match_start = matches[i+1].start()
                    extracted_text = block[start_pos:next_match_start].strip()
                else:  # If the last wine
                    extracted_text = block[start_pos:].strip()

                    # Trim any residual winery information
                    winery_info_start = re.search(r'wineryname', extracted_text)
                    if winery_info_start:
                        extracted_text = extracted_text[:winery_info_start.start()].strip()

            
            # Remove any prefix from the extracted text
            prefix_pattern = r'\b(?:' + '|'.join(re.escape(prefix) for prefix in wine_name_prefixes) + r')\b'
            extracted_text = re.sub(prefix_pattern, '', extracted_text).strip()

            # Replace newline characters with spaces
            extracted_text = extracted_text.replace('\n', ' ').replace('- ', '').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')

            if i < len(matches) - 1:  # If not the last wine
                wine_text_segment = block[match.end():matches[i+1].start()]
            else:  # If the last wine
                wine_text_segment = block[match.end():]

            # Extract bottle number from the specific wine text segment
            bottle_match = re.search(r'Bt\. ([\d\.,]+)', wine_text_segment)
            if bottle_match:
                raw_bottle_number = int(bottle_match.group(1).replace('.', '').replace(',', ''))
                bottle_number = str(raw_bottle_number // 1000)
            else:
                bottle_number = None

            # Extract maturation details
            maturation_match = re.search(r'Mat\. ([^\n]+)', wine_text_segment)
            maturation_details = maturation_match.group(1) if maturation_match else None


            if winery_name:
                entries.append((winery_name, wine_name, vintage, prefix_matched, price, extracted_text, grapes, alcohol_content, bottle_number, maturation_details))

    return entries


def extract_pairing_text(text):
    """Extracts the part of the text between the last full stop and the penultimate full stop."""
    sentences = text.split(".")
    if len(sentences) > 1:
        pairing_text = sentences[-2].strip()
        main_text = ".".join(sentences[:-2] + [sentences[-1]]).strip()
        return main_text, pairing_text
    else:
        return text, None



def write_to_csv(entries):
    columns = ['Entry', 'Ref', 'OLDRS', 'RANK', 'RS', 'RAWQP', 'QPRANK', 'QP', 'RANK2', 'RS2', 'RAWQP2', 'QP2', 
               'RANK3', 'RS3', 'RAWQP3', 'QP3', 'RawAvg', 'RatingYear', 'Vintage', 'Qterms', 'FullName', 
               'AppellationLevel', 'AppellationName', 'WineryName', 'Region', 'EvaluationAvg', 'Price', 'Grapes', 
               'Pairing', 'ScoreAvg', 'EvaluationAIS', 'ScoreAIS', 'EvaluationGR', 'ScoreGR', 'SLC', 'TLC', 
               'WineTypeIT', 'WineType', 'Alcohol', 'Bottles', 'AgingMonths', 'AgingTypeIT', 'AgingType',
               'Tasting', 'Notes', 'Country', 'VintageNV', 'Method', 'Sweetness']

    with open(f'static/pdf/vitae24-{region}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for winery_name, wine_name, vintage, wine_prefix, price, extracted_text, grapes, alcohol_content, bottle_number, maturation_details in entries:
            row = [''] * len(columns)
            row[columns.index('FullName')] = wine_name
            row[columns.index('WineryName')] = winery_name
            row[columns.index('Vintage')] = vintage
            row[columns.index('Alcohol')] = alcohol_content
            row[columns.index('Bottles')] = bottle_number
            row[columns.index('ScoreAIS')] = scoreAIS_mapping[wine_prefix]
            row[columns.index('AgingTypeIT')] = maturation_details
            row[columns.index('Price')] = price
            row[columns.index('Grapes')] = grapes
            # Fixed values
            row[columns.index('RatingYear')] = '2024'
            row[columns.index('Entry')] = '2'
            row[columns.index('Region')] = region.capitalize()
            row[columns.index('Country')] = 'Italy'
            row[columns.index('EvaluationGR')] = 'nd'
            row[columns.index('ScoreGR')] = 'nd'
            
            # Determine where to place the extracted text
            main_text, pairing_text = extract_pairing_text(extracted_text)
            row[columns.index('Tasting')] = main_text if len(main_text) > 100 else None
            row[columns.index('Pairing')] = pairing_text
            
            writer.writerow(row)

if len(sys.argv) > 1:
    region = sys.argv[1]
else:
    region = input("Enter the region: ")

with open(f'static/pdf/vitae24-{region}.txt', 'r') as file:
    content = file.read()
    entries = extract_winery_and_wine_names(content)
    write_to_csv(entries)