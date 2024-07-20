import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm, A4
from reportlab.lib.units import mm
import os
import qrcode
from datetime import datetime
from flask import send_file

current_date = datetime.now()
output_directory = current_date.strftime("%Y-%m-%d")
output_pdf_path = "output.pdf"


def create_qr_codes(file, pagesize, billwidth, billheight, billrows, billcolumns):
    """Create a list of QR codes from the given input pdf files.
    """
    try:
        lines = extract_text_and_qrcode_from_pdf(file)
        reconstructed_data = reconstruct_text(lines)
        words = extract_words(reconstructed_data)
        formatted_text = add_meaningful_spaces(words)
        path = create_new_pdf_with_lines(output_pdf_path, formatted_text, pagesize, billwidth, billheight, billrows, billcolumns)
        return path
    except Exception as e:
        # Handle any other exceptions not caught by the previous except blocks
        print(f"Error occurred: {e}")

def extract_text_and_qrcode_from_pdf(file):
    file_path = file.filename
    file.save(file_path)
    file_data = open(file_path, "rb")
    reader = PyPDF2.PdfReader(file_data)
    num_pages = len(reader.pages)
    texts = ""
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        texts += page.extract_text()
    word = texts.split()
    return word

def create_new_pdf_with_lines(output_pdf_path, bills_data, pagesize, billwidth, billheight, billrows, billcolumns):
    try:
        os.makedirs(f"{output_directory}", exist_ok=True)
        size = eval(pagesize)
        width = int(size[0]) * mm 
        height = int(size[1]) * mm  
        # Use A4 size for landscape orientation
        c = canvas.Canvas(f"{output_directory}/{output_pdf_path}", pagesize=(width, height))
        file_path = f"{output_directory}/{output_pdf_path}"
        # Calculate positions for bills in a 3x6 grid with spacing
        bill_width = width / int(billcolumns)
        bill_height = height / int(billrows)
        x_positions = [0, bill_width, bill_width * 2, bill_width * 3]
        y_positions = [0, bill_height, bill_height * 2, bill_height * 3, bill_height * 4, bill_height * 5, bill_height * 6, bill_height * 7, bill_height * 8]

        bills_per_page = int(billcolumns) * int(billrows)  # 3 columns x 8 rows = 24 bills per page
        num_bills = len(bills_data)
        num_pages = (num_bills // bills_per_page) + 1

        for page_num in range(num_pages):
            c.showPage()
            c.setFont("Helvetica", 6)
            for i in range(bills_per_page):
                index = page_num * bills_per_page + i
                # print(page_num, index, bills_per_page, i)
                if index >= num_bills:
                    break
                row = i // int(billcolumns)
                col = i % int(billcolumns)
                x_offset = x_positions[col]
                y_offset = y_positions[row]

                original_string = bills_data[index][0]
                split_strings = original_string.split(",")
                formatted_list = [s.strip() for s in split_strings]
                qr_code_path = f"{output_directory}/{formatted_list[-1]}.png"
                make_qr_code(formatted_list[-1], qr_code_path)

                # Draw QR code, 
                print(x_offset + 30 * mm, y_offset + bill_height - 20 * mm, y_offset, bill_height)
                c.drawImage(qr_code_path, x_offset + 30 * mm, y_offset + bill_height - 20 * mm, width=20 * mm, height=20 * mm)

                # Draw text
                x_text_offset = x_offset + 3 * mm
                y_text_offset = y_offset + bill_height - 4 * mm
                line_height = 3 * mm
                if len(formatted_list) == 5 or len(formatted_list) == 4:
                    for line in formatted_list:
                        c.drawString(x_text_offset, y_text_offset, line)
                        y_text_offset -= line_height
                
                # Remove QR code file after use
                if os.path.exists(qr_code_path):
                    os.remove(qr_code_path)

                # Draw horizontal lines separating bills
                if col < 4:
                    c.line(x_positions[col] + bill_width, y_offset, x_positions[col] + bill_width, y_offset + bill_height)
        c.save()
        print(f"PDF saved as {file_path}")
        return file_path
    except Exception as e:
        # Handle any other exceptions not caught by the previous except blocks
        print(f"Error occurred while pdf file generate: {e}")

def reconstruct_text(data):
    reconstructed_data = []
    current_entry = []
    for item in data:
        current_entry.append(item)
        if item.startswith("INPEPE"):
            # Once the current entry is complete, merge the fragments and add to reconstructed_data
            reconstructed_data.append("".join(current_entry))
            current_entry = []
    return combine_strings(reconstructed_data)

def extract_words(reconstructed_data):
    words = []
    for entry in reconstructed_data:
        # Split entry into words based on the delimiter (space, hyphen, colon, etc.)
        words.extend(entry.split())
    return words


def combine_strings(data):
    combined_list = []
    current_string = ""
    
    for item in data:
        if "Box" in item:
            if current_string:
                combined_list.append(current_string)
            current_string = item
        else:
            current_string += item
    
    # Append the last accumulated string
    if current_string:
        combined_list.append(current_string)
    
    return combined_list


def add_meaningful_spaces(lines):
    # Split the text by new lines
    # lines = text.strip().splitlines()

    formatted_lines = []
    for line in lines:
        # Replace characters to add spaces at meaningful places
        line = line.replace("L2Building:", "L2, Building:E1, ")
        line = line.replace("L3SAFEX", "L3, SAFEX")
        line = line.replace("E1SAFEX-", "SAFEX-")
        line = line.replace("(100GRM)", "(100 GRM),")
        line = line.replace("Box:", " Box:")
        line = line.replace("INPEPE1X", ", INPEPE1X")
        formatted_lines.append([line])
    # print(formatted_lines)
    return formatted_lines


def make_qr_code(qr_number, qr_code_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_number)
    qr.make(fit=True)
    # Create an image from the QR code instance
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(qr_code_path)
    return qr_img



    