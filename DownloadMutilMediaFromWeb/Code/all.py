import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from urllib.parse import urlparse
import re
from collections import deque
import time

def create_output_dir(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '-')
    
    base_dir = domain
    output_dir = base_dir
    counter = 1
    
    while os.path.exists(output_dir):
        if counter == 1:
            return output_dir
        output_dir = f"{base_dir}-{counter}"
        counter += 1
    
    os.makedirs(output_dir)
    return output_dir

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def create_subdirectory(base_dir, url):
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    if not path:
        path = 'home'
    safe_path = sanitize_filename(path)
    sub_dir = os.path.join(base_dir, safe_path)
    os.makedirs(sub_dir, exist_ok=True)
    return sub_dir

def download_media(url, output_dir):
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

def crawl_website(start_url):
    base_output_dir = create_output_dir(start_url)
    print(f"Thư mục gốc: {base_output_dir}")

    parsed_start_url = urlparse(start_url)
    base_url = f"{parsed_start_url.scheme}://{parsed_start_url.netloc}"

    visited = set()
    to_visit = deque([start_url])

    while to_visit:
        current_url = to_visit.popleft()
        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"Đang crawl: {current_url}")

        # Tạo thư mục con cho URL hiện tại
        current_output_dir = create_subdirectory(base_output_dir, current_url)
        print(f"Đang tải xuống vào thư mục: {current_output_dir}")

        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            download_media(current_url, current_output_dir)

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urllib.parse.urljoin(base_url, href)
                if full_url.startswith(base_url) and full_url not in visited:
                    to_visit.append(full_url)

            # Thêm delay để tránh quá tải server
            time.sleep(1)

        except requests.RequestException as e:
            print(f"Lỗi khi crawl {current_url}: {e}")

    print(f"Hoàn tất! Tất cả tệp đã được tải vào {base_output_dir}")

url = input("Nhập URL của bạn: ")
crawl_website(url)