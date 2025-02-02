# pip install -r requirements.txt
# test string: 868714043166906 806FB09F19B5 SU20'0301
# pyinstaller --onefile --add-data "C:\Windows\Fonts\arial.ttf;Fonts" main.py

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageWin
import tkinter as tk
from tkinter import messagebox
import win32ui, win32print
from utils import eval_qr_data, generate_image_with_barcodes, get_font_path

###############################################################################
###############################################################################
###############################################################################

def on_enter(event):
    input_data = event.widget.get().strip()
    if input_data:
        result = eval_qr_data(input_data)
        if result.get("valid"):
            generate_image_with_barcodes("qr_with_barcodes.png", result)
            #messagebox.showinfo("Result", f"IMEI: {result.get('imei')}\nAddress: {result.get('address')}\nECU Code: {result.get('ecu_code')}")
            printer_name = read_printer_name("printer_name.txt")
            print_image("qr_with_barcodes.png", printer_name)
        event.widget.delete(0, tk.END)

def create_input_window():
    window = tk.Tk()
    window.title("Attesa del Codice")
    window.geometry("800x200")  # Imposta la dimensione della finestra    
    label = tk.Label(window, text="In attesa del codice:", font=("Arial", 16))
    label.pack(pady=20)    
    entry = tk.Entry(window, width=50, font=("Arial", 14))
    entry.pack(pady=20)
    #entry.insert(0, "868714043166906 806FB09F19B5 SU20'0301")  # Imposta il testo predefinito
    entry.focus_set()
    entry.bind("<Return>", on_enter)    
    window.mainloop()

def list_printers():
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    for printer in printers:
        print(f"Printer Name: {printer[2]}")

def read_printer_name(file_path):
    try:
        with open(file_path, 'r') as file:
            printer_name = file.readline().strip()
            print(f"Printer name read from file: {printer_name}")
            return printer_name
    except Exception as e:
        print(f"Error reading printer name: {e}")
        return None

def print_image(image_path, printer_name):
    if os.path.exists(image_path):
        try:
            print(f"Setting default printer to: {printer_name}")
            win32print.SetDefaultPrinter(printer_name)
            
            # 📏 Dimensioni etichetta in millimetri
            label_width_mm = 70
            label_height_mm = 30

            # 🖨 Ottieni informazioni sulla stampante
            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            printer_dc = win32ui.CreateDC()
            printer_dc.CreatePrinterDC(printer_name)

            # 🔍 Ottieni DPI della stampante (Punti per Pollice)
            printer_dpi = printer_dc.GetDeviceCaps(88)  # HORZRES
            print_dpi = printer_dc.GetDeviceCaps(90)  # LOGPIXELSX (DPI)

            # 📏 Converti millimetri in unità di stampa
            mm_to_inch = 25.4  # 1 inch = 25.4 mm
            label_width_px = int((label_width_mm / mm_to_inch) * print_dpi)
            label_height_px = int((label_height_mm / mm_to_inch) * print_dpi)

            # 📸 Apri e ridimensiona l'immagine
            image = Image.open(image_path)
            image = image.resize((label_width_px, label_height_px))

            # 🖼 Converti immagine per stampa
            dib = ImageWin.Dib(image)

            # 🖨 Stampa
            printer_dc.StartDoc("Etichetta 70x30mm")
            printer_dc.StartPage()

            # 📍 Stampa immagine centrata (modifica x, y se necessario)
            x, y = 10, 5  # Posizione di stampa in unità della stampante
            dib.draw(printer_dc.GetHandleOutput(), (x, y, x + label_width_px, y + label_height_px))

            # ✅ Termina stampa
            printer_dc.EndPage()
            printer_dc.EndDoc()
            printer_dc.DeleteDC()
            print("Print command executed")
        except Exception as e:
            print(f"Error printing image: {e}")
    else:
        print(f"Image file not found: {image_path}")
    
###############################################################################
###############################################################################
###############################################################################
    
if __name__ == "__main__":
    try:
        font = ImageFont.truetype(get_font_path(), 20)
        print("Font caricato con successo")
    except OSError:
        print("Errore: impossibile aprire la risorsa del font")

    list_printers()
    create_input_window()
