import tkinter as tk
import json
from PIL import Image, ImageTk
from utils import generate_image_with_barcodes, get_font_path
import barcode
from barcode.writer import ImageWriter
import barcode
from PIL import Image, ImageWin, ImageDraw, ImageFont
import qrcode

data = {
    "imei": "868714043166906",
    "address": "806FB09F19B5",
    "ecu_code": "SU20'0301"
}

coordinates = {
    "IMEI": (20, 45),
    "IMEI_barcode": (120, 20),
    "BLE MAC\nADDRESS": (20, 135),
    "Address_barcode": (120, 120),
    "ECU CODE": (20, 280),
    "SU20'0301": (200, 280),
    "QRCode": (590, 130)
}

def generate_image_with_barcodes(data):
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

    # Carica e genera barcode per Address
    address_barcode = barcode.get('code128', data["address"], writer=ImageWriter())
    writer_options = {
        'module_width': 0.18,
        'module_height': 3.7,
        'font_size': 7,
        'text_distance': 3,
        'quiet_zone': 6.5,
        'background': 'white',
        'foreground': 'black',
        'write_text': True,
        'font_path': font_path,
        'format': 'PNG'
    }
    address_barcode_image = address_barcode.render(writer_options=writer_options)
    
    # Carica e genera barcode per IMEI
    imei_barcode = barcode.get('code128', data["imei"], writer=ImageWriter())
    imei_barcode_image = imei_barcode.render(writer_options=writer_options)
    
    return address_barcode_image, imei_barcode_image

def save_positions():
    with open("coords.json", "w") as f:
        json.dump(coordinates, f, indent=2)

def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_move(event):
    widget = event.widget
    dx = event.x - widget._drag_start_x
    dy = event.y - widget._drag_start_y
    x = widget.winfo_x() + dx
    y = widget.winfo_y() + dy
    widget.place(x=x, y=y)
    for key, val in coordinates.items():
        if getattr(widget, 'name', None) == key:
            coordinates[key] = (x, y)

root = tk.Tk()
root.title("Editor posizioni")
root.geometry("800x500")

address_barcode_image, imei_barcode_image = generate_image_with_barcodes(data)

for key, (x, y) in coordinates.items():
    if key == "Address_barcode":
        barcode_photo = ImageTk.PhotoImage(address_barcode_image)
        lbl = tk.Label(root, image=barcode_photo)
        lbl.image = barcode_photo  # Keep a reference to avoid garbage collection
    elif key == "IMEI_barcode":
        barcode_photo = ImageTk.PhotoImage(imei_barcode_image)
        lbl = tk.Label(root, image=barcode_photo)
        lbl.image = barcode_photo  # Keep a reference to avoid garbage collection
    else:
        lbl = tk.Label(root, text=key, bg="lightblue")
    lbl.name = key
    lbl.place(x=x, y=y)
    lbl.bind("<Button-1>", on_drag_start)
    lbl.bind("<B1-Motion>", on_drag_move)

tk.Button(root, text="Salva Posizioni", command=save_positions).pack(side="bottom")

root.mainloop()