import os
import pyqrcode
import png
from pyqrcode import QRCode
from urllib.parse import urlparse

# Ensure the 'image' directory exists
if not os.path.exists('image'):
    os.makedirs('image')

print('')
s = input("Enter your URL: ")

# Parse the URL to get the domain and path
parsed_url = urlparse(s)
domain_name = parsed_url.netloc
path = parsed_url.path.strip('/')

# Remove 'www.' if it is part of the domain
domain_name = domain_name.replace('www.', '')

# Construct the filename using the domain and path
filename = domain_name
if path:
    filename += '-' + path.replace('/', '-')

file_path = os.path.join('image', f'{filename}.png')

# Create QR code
url = pyqrcode.create(s)

# Save the QR code image with the domain and path as the filename
url.png(file_path, scale=6)

print(f"QR code saved as {file_path}")
