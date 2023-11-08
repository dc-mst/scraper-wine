import xml.etree.ElementTree as ET

# Function to parse XML and write to text file
def xml_to_text(xml_file, txt_file):
    # Parse XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Open the text file for writing
    with open(txt_file, 'w', encoding='utf-8') as f:
        # Iterate over each textbox element in the XML
        for textbox in root.findall('.//textbox'):
            # Collect text from each text element within textbox
            line_texts = []
            for textline in textbox.findall('.//textline'):
                for text in textline:
                    # Check if text contains actual characters or it is just a space
                    if text.text and text.text.strip() != '':  # Non-empty text
                        line_texts.append(text.text)
                    elif text.text:  # Just a space
                        line_texts.append(' ')
            # Join all collected text elements and write to the file
            f.write(''.join(line_texts).replace('  ', ' ') + '\n')

# Call the function with the path to your XML file and the output text file
xml_to_text('static/pdf/vitae22-piemonte.xml', 'static/pdf/vitae22-piemonte.txt')