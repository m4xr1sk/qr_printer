import json
import os
import re
import sys
import barcode
from barcode.writer import ImageWriter
import barcode
from PIL import Image, ImageWin, ImageDraw, ImageFont
import qrcode


def get_font_path():
    if getattr(sys, 'frozen', False):  # Se eseguito come .exe
        base_path = sys._MEIPASS  # PyInstaller unpacking path
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, "Fonts", "arial.ttf")

def load_coordinates(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {file_path} non trovato. Utilizzo delle coordinate predefinite.")
        return {
            "IMEI_label": (20, 45),
            "IMEI_barcode": (120, 20),
            "IMEI_text": (150, 80),
            "Address_label": (20, 135),
            "Address_barcode": (120, 120),
            "Address_text": (150, 180),
            "ECU_label": (20, 280),
            "ECU_text": (200, 280),
            "QRCode": (590, 130)
        }


def generate_image_with_barcodes(image_name, qr_data):
    # Coordinate Table    
    coordinates = load_coordinates("coords.json")

    sizes = {
        "Image": (800, 350),
        "QRCode": (200, 200),
    }
    
    # Assicurati di caricare il font prima di passarlo ai barcode writer_options
    font_path = get_font_path()

    try:
        test_font = ImageFont.truetype(font_path, 7)  # Test se il font è caricabile
    except OSError:
        print(f"Errore: impossibile aprire la risorsa del font {font_path}")
        
    try:
        font_label = ImageFont.truetype(get_font_path(), 30)
    except IOError:
        font_label = ImageFont.load_default()

    try:
        font_text = ImageFont.truetype(get_font_path(), 30)
    except IOError:
        font_text = ImageFont.load_default()

    # Carica e genera barcode per IMEI, Address ed ECU Code
    imei_barcode = barcode.get('code128', qr_data['imei'], writer=ImageWriter())
    address_barcode = barcode.get('code128', qr_data['address'], writer=ImageWriter())
    writer_options={
        'module_width': 0.18,
        'module_height': 3.7,
        'font_size': 7,
        'text_distance': 3,
        'quiet_zone': 6.5,
        'background': 'white',
        'foreground': 'black',
        'write_text': True,
        'font_path': font_path,
        'format': 'PNG'}
    imei_barcode_image = imei_barcode.render(writer_options=writer_options)    
    address_barcode_image = address_barcode.render(writer_options=writer_options)

    # Genera il QR Code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2
    )
    qr.add_data(qr_data['imei'] + " " + qr_data['address'] + " " + qr_data['ecu_code'])
    qr.make(fit=True)
    qr_image = qr.make_image(fill='black', back_color='white').resize(sizes["QRCode"])

    # Crea una nuova immagine bianca 
    new_image = Image.new('RGB', sizes["Image"], 'white')
    draw = ImageDraw.Draw(new_image)

    new_image.paste(imei_barcode_image, coordinates["IMEI_barcode"])
    new_image.paste(address_barcode_image, coordinates["Address_barcode"])

    # Primo Riga: IMEI
    draw.text(coordinates["IMEI_label"], "IMEI", fill="black", font=font_label)
    #draw.text(coordinates["IMEI_text"], qr_data['imei'], fill="black", font=font_text)

    # Seconda Riga: BLE MAC ADDRESS
    draw.text(coordinates["Address_label"], "BLE MAC\nADDRESS", fill="black", font=font_label)
    #draw.text(coordinates["Address_text"], qr_data['address'], fill="black", font=font_text)

    # Terza Riga: ECU CODE
    draw.text(coordinates["ECU_label"], "ECU CODE", fill="black", font=font_label)
    draw.text(coordinates["ECU_text"], qr_data['ecu_code'], fill="black", font=font_text)

    # Incolla il QR Code sulla destra
    new_image.paste(qr_image, coordinates["QRCode"])

    # Salva la nuova immagine
    new_image.save(image_name)
    print("Immagine generata: " + image_name)


def eval_qr_data(data):    
    print("QR Data:", data)
    pattern = r'^(\d{15})\s([A-F0-9]{12})\s([A-Z]{2}\d{2}\'\d{4})$'
    data = re.sub(r"[àèéìòù]", "'", data)
    match = re.match(pattern, data.strip())
    # Validazione del formato QR
    match = re.match(pattern, data.strip())
    if match:
        imei, address, ecu_code = match.groups()
        print("IMEI:", imei)
        print("Address:", address)
        print("ECU Code:", ecu_code)
        return {
            "data": data,
            "imei": imei,
            "address": address,
            "ecu_code": ecu_code,
            "valid": True
        }
    else:
        print("Invalid QR Data")
        return {
            "data": data,
            "valid": False
        }

