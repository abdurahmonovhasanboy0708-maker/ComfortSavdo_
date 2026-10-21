
import sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H

url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_H,
    box_size=14,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="#0a7d5a", back_color="white").convert("RGB")
img.save("comfort_savdo_qr.png")

print(f"Tayyor: comfort_savdo_qr.png  ->  {url}")