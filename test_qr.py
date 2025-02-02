import math
import barcode
from barcode.writer import ImageWriter
from pyzbar.pyzbar import decode
import cv2
from utils import eval_qr_data, generate_image_with_barcodes


def read_qr_from_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break        
        for barcode in decode(frame):
            data = barcode.data.decode('utf-8')            
            res = eval_qr_data(data)
        cv2.imshow("QR Reader", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break    
    cap.release()
    cv2.destroyAllWindows()


def read_qr_from_file(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not open or find the image:", image_path)
        return
    
    qr_codes = [barcode for barcode in decode(img) if barcode.type == "QRCODE"]
    
    if not qr_codes:
        print("No QR codes found.")
        return
    
    # Dimensioni dell'immagine
    height, width, _ = img.shape
    center_x, center_y = width / 2, height / 2

    # Funzione per calcolare la distanza dal centro
    def distance(bracket):
        x, y, w, h = bracket
        qr_center_x = x + w / 2
        qr_center_y = y + h / 2
        return math.sqrt((qr_center_x - center_x) ** 2 + (qr_center_y - center_y) ** 2)
    
    # Trova il QR code più vicino al centro
    central_qr = min(qr_codes, key=lambda qr: distance(qr.rect))
    
    data = central_qr.data.decode('utf-8')    
    return eval_qr_data(data)


if __name__ == "__main__":
    #read_qr_from_camera()
    if 1 == 1:
        result = read_qr_from_file("test_images/qr_all.jpg")
        if result and result.get("valid"):
            generate_image_with_barcodes("qr_with_barcodes.png", result)                
