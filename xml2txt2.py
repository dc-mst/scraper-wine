import xml.etree.ElementTree as ET
import re

# Function to convert XML to text
def xml_to_text_grouped(xml_file, txt_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    less_than_240 = []
    greater_or_equal_240 = []

    for page in root.findall('.//page'):
        added_less_than_240 = False
        added_greater_or_equal_240 = False
        line_counter_less_than_240 = 0
        line_counter_greater_or_equal_240 = 0

        for textbox in page.findall('.//textbox'):
            if textbox.find('.//layout'):
                continue
            bbox = textbox.attrib.get('bbox', '')
            bbox_parts = bbox.split(',')
            if float(bbox_parts[3]) <= 65.002:
                continue
            if float(bbox_parts[3]) == 637.795:
                continue
            if float(bbox_parts[3]) == 633.589:
                continue
            line_texts = []
            bbox = textbox.attrib.get('bbox', None)
            if bbox:
                bbox_values = list(map(float, bbox.split(',')))
                for textline in textbox.findall('.//textline'):
                    for text in textline:
                        if text.text and text.text.strip():
                            line_texts.append(text.text)
                        elif text.text:
                            line_texts.append(' ')
                text_content = ''.join(line_texts).replace('  ', ' ')
                if bbox_values and bbox_values[0] < 240:
                    if not added_less_than_240:
                        less_than_240.append("WINERYEND")
                        added_less_than_240 = True
                        line_counter_less_than_240 = 0
                    if line_counter_less_than_240 not in [1, 2, 3]:
                        less_than_240.append(text_content)
                    line_counter_less_than_240 += 1
                else:
                    if not added_greater_or_equal_240:
                        greater_or_equal_240.append("WINERYEND")
                        added_greater_or_equal_240 = True
                        line_counter_greater_or_equal_240 = 0
                    if line_counter_greater_or_equal_240 not in [1, 2, 3]:
                        greater_or_equal_240.append(text_content)
                    line_counter_greater_or_equal_240 += 1

    # Combine the lists
    combined_text = less_than_240 + greater_or_equal_240

    # Remove consecutive empty lines
    final_text = []
    prev_line_empty = False
    for line in combined_text:
        if line.strip() == '':  # Check if the line is empty or contains only whitespace
            if prev_line_empty:
                continue  # Skip adding the line if the previous line was also empty
            prev_line_empty = True
        else:
            prev_line_empty = False
        final_text.append(line)

    with open(txt_file, 'w') as f:
        f.write('\n'.join(final_text))

# Function to apply regex operations
def apply_regex_operations(txt_file):
    # Read the content of the file
    with open(txt_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Apply all the regex replacements
    content = re.sub(r'  \n', ' ', content)
    content = re.sub(r'mesi(?!.*mesi) (.*)\n', r'mesi\n\1\n', content)
    content = re.sub(r'([a-z])- ', r'\1', content)
    content = re.sub(r'Ferm\. Acciaio (?!.*\|)(.*)', r'Ferm. Acciaio\n\1', content)
    content = re.sub(r'\n(sui .*)', r' \1', content)
    content = re.sub(r'lieviti(?!.*lieviti) (.*)\n', r'lieviti\n\1\n', content)
    content = re.sub(r'\) \n', ') ', content)

    # Write the modified content back to the file
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Path to the XML and TXT files
xml_file_path = 'static/pdf/vitae22-piemonte.xml'
txt_file_path = 'static/pdf/vitae22-piemonte.txt'

# Convert XML to grouped text
xml_to_text_grouped(xml_file_path, txt_file_path)

# Apply the regex operations to the grouped text file
apply_regex_operations(txt_file_path)