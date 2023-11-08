import xml.etree.ElementTree as ET


user_input = input("Enter the string to replace [x]: ")

# File paths
input_file_path = f'static/pdf/vitae22-{user_input}.xml'
output_file_path = f'static/pdf/vitae22-{user_input}.txt'

# Read the XML content from the file
with open(input_file_path, 'r', encoding='utf-8') as file:
    xml_content = file.read()

# Parse the XML content
root = ET.fromstring(xml_content)

# Open the output TXT file
with open(output_file_path, 'w', encoding='utf-8') as file:

    # Iterate through each 'page' tag in the XML
    for page in root.findall('.//page'):
        first_column_texts = []  # Texts from the first column
        second_column_texts = []  # Texts from the second column

        # Iterate through all the 'textbox' tags within each 'page'
        for textbox in page.findall('.//textbox'):
            # Get the bbox attribute
            bbox = textbox.attrib.get('bbox', '')
            bbox_parts = bbox.split(',')

            # Check if bbox matches the patterns to exclude
            if bbox.startswith('39.685,') and bbox.endswith(',602.923'):
                continue  # Skip this textbox
            if bbox.startswith('240.945,') and bbox.endswith(',602.923'):
                continue  # Skip this textbox
            if bbox.startswith('16.700,') and bbox_parts[2] == '23.300':
                continue  # Skip this textbox
            if float(bbox_parts[3]) <= 58.002:
                continue  # Skip this textbox

            # Check the first <text> element content only if the bbox starts with '39.685'
            if bbox.startswith('39.685,') or bbox.startswith('240.945,'):
                first_text_element = textbox.find('.//text')
                if first_text_element is not None and first_text_element.text == "i":
                    continue  # Skip this textbox

            if bbox.startswith('136.772,') or bbox.startswith('338.031'):
                first_text_element = textbox.find('.//text')
                if first_text_element is not None and first_text_element.text == "p":
                    continue  # Skip this textbox

            # Sort text into columns based on the x coordinate
            text_content = ''
            for textline in textbox.findall('.//text'):
                text_content += textline.text if textline.text else ''

            if text_content:  # Check if text_content is not empty
                if float(bbox_parts[0]) < 240:
                    first_column_texts.append(text_content)
                else:
                    second_column_texts.append(text_content)

        if second_column_texts:
            first_column_texts.append("WINERYEND\nWINERYSTART\n")

        page_text = ' '.join(first_column_texts + second_column_texts)

        # Write the page text to the output TXT file
        if page_text:  # Check if page_text is not empty
            file.write(page_text)

        # Write "ENDPAGE" at the end of each page
        file.write("\nWINERYEND\nWINERYSTART\n")