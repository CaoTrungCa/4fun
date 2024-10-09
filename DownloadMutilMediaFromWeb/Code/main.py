import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from urllib.parse import urlparse
import re

def create_output_dir(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '-')
    
    base_dir = domain
    output_dir = base_dir
    counter = 1
    
    while os.path.exists(output_dir):
        if counter == 1:
            return output_dir  # Nếu thư mục đã tồn tại, sử dụng nó
        output_dir = f"{base_dir}-{counter}"
        counter += 1
    
    os.makedirs(output_dir)
    return output_dir

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_media(url):
    output_dir = create_output_dir(url)
    print(f"Đang tải xuống vào thư mục: {output_dir}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        media_tags = soup.find_all(['img', 'video', 'source'])

        for tag in media_tags:
            media_url = tag.get('src') or tag.get('href')

            if media_url:
                media_url = urllib.parse.urljoin(url, media_url)

                try:
                    parsed_url = urlparse(media_url)
                    filename = os.path.basename(parsed_url.path)
                    
                    if not filename:
                        print(f"Bỏ qua: {media_url} (không có tên file)")
                        continue
                    
                    filename = sanitize_filename(filename)
                    full_path = os.path.join(output_dir, filename)

                    if os.path.exists(full_path):
                        print(f"Bỏ qua: {filename} (file đã tồn tại)")
                        continue

                    media_response = requests.get(media_url)
                    media_response.raise_for_status()

                    with open(full_path, 'wb') as f:
                        f.write(media_response.content)

                    print(f"Đã tải: {full_path}")
                except requests.RequestException as e:
                    print(f"Lỗi khi tải {media_url}: {e}")
                except OSError as e:
                    print(f"Lỗi khi lưu tệp {filename}: {e}")

    except requests.RequestException as e:
        print(f"Lỗi khi tải trang web: {e}")

    print(f"Hoàn tất! Tất cả tệp đã được tải vào {output_dir}")

url = input("Nhập URL của bạn: ")
download_media(url)