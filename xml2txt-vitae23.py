import subprocess
import xml.etree.ElementTree as ET
import sys

def consolidate_pdf_to_text(filename: str):
    subprocess.run(["pdf2txt.py", f"-o vitae23-{filename}.xml", "-t", "xml", f"vitae23-{filename}.pdf"])

def extract_text_with_color(textbox_element):
    reconstructed_text = []

    for textline in textbox_element.findall('textline'):
        line_text = []
        current_color = None
        current_segment = []

        for text in textline.findall('text'):
            if text.text:
                color = text.attrib.get('ncolour', 'unknown')

                if color != current_color:
                    if current_segment:
                        segment_content = ''.join(current_segment)
                        if "aaaa" in segment_content and current_color != 'unknown' and current_color != '[0]':
                            line_text.append(f"{segment_content}[color: {current_color}]")
                        else:
                            line_text.append(segment_content)
                        current_segment = []
                    current_color = color

                current_segment.append(text.text)

        if current_segment:
            segment_content = ''.join(current_segment)
            if "aaaa" in segment_content and current_color != 'unknown' and current_color != '[0]':
                line_text.append(f"{segment_content}[color: {current_color}]")
            else:
                line_text.append(segment_content)

        reconstructed_text.append(" ".join(line_text).strip())

    return "\n".join(reconstructed_text)


def organize_text_by_columns(page_element):
    textboxes = sorted(page_element.findall('textbox'), key=lambda e: float(e.attrib['bbox'].split(',')[0]))

    column1, column2 = [], []

    # List of bbox values to exclude
    exclude_bboxes = ["36.850,", "135.358,", "240.946,", "339.454,"]

    for textbox in textboxes:
        bbox_values = [float(val) for val in textbox.attrib['bbox'].split(',')]
        y_coord = bbox_values[1]

        # Extract the text for the current textbox
        extracted_text = extract_text_with_color(textbox)

        # Exclude if it contains both "Viticoltura:" and "Ettari:"
        if "Viticoltura:" in extracted_text and "Ettari:" in extracted_text:
            continue

        if "www" in extracted_text:
            continue

        # Exclude only if it matches the bbox and is in the bottom part of the page
        if any(textbox.attrib['bbox'].startswith(exclude_bbox) for exclude_bbox in exclude_bboxes) and y_coord < 100:
            continue

        x_coord = float(textbox.attrib['bbox'].split(',')[0])

        # Check if the textbox matches the bbox for which you want to prepend "wineryname"
        if 610 < y_coord < 635:  # Updated condition based on the provided bbox y-coordinates
            extracted_text = "wineryname " + extracted_text

        if x_coord < 240:
            column1.append(extracted_text)
        else:
            column2.append(extracted_text)

    # Combine column1's content, add the "COLUMNEND" string, and then add column2's content
    return "\n".join(column1 + ["WINERYEND"] + column2)


def extract_text_from_page(page_element):
    return organize_text_by_columns(page_element)

# Load and parse the XML
xml_path = f"static/pdf/vitae23-{sys.argv[1]}.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

pages = root.findall('.//page')

final_text = []
for page in pages:
    page_text = extract_text_from_page(page)
    final_text.append(page_text)
    final_text.append("WINERYEND")

# Join the text for all pages and print
text_content = "\n".join(final_text)

# Remove color strings
text_content = text_content.replace("[color: [0.155]]", "").replace("[color: [0.076]]", "")

print(text_content)

# Optionally, save the extracted text to a file
with open(f"static/pdf/vitae23-{sys.argv[1]}.txt", "w", encoding="utf-8") as f:
    f.write(text_content)
