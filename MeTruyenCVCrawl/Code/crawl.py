import json
import os
import re
from urllib.parse import urlparse
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

def create_folder_from_url(url):
    parsed_url = urlparse(url)
    folder_name = parsed_url.path.strip("/").split("/")[-1]
    folder_name = re.sub(r'[\\/*?:"<>|]', "_", folder_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def extract_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

def create_json_files(folder_name):
    filename = "chapter_links.json"
    file_path = os.path.join(folder_name, filename)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

def create_chapter_viewer_html(folder_name, story_title):
    chapter_viewer_file = os.path.join(folder_name, "chapter_viewer.html")
    with open(chapter_viewer_file, 'w', encoding='utf-8') as f:
        f.write(create_html_content(story_title))

def create_html_content(story_title):
    style = '''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playwrite+VN&display=swap');

        @import url("https://fonts.googleapis.com/css2?family=Potta+One&display=swap");

        body {
            font-family: 'Playwrite VN', cursive;
            line-height: 1.6;
            color: #333;
            max-width: 1280px;
            margin: 0 auto;
            padding: 20px;
        }

        h1 {
            position: fixed;
            top: -22px;
            padding: 10px 0;
            text-align: center;
            width: 1280px;
            background-color: #fff;
            color: #2c3e50;
            box-shadow: 0px -3px 14px -3px rgba(8, 5, 5, 0.28);
        }

        svg {
            font-family: "Potta One", sans-serif;
            width: 100%;
            height: 100%;
        }

        svg text {
            animation: stroke 5s infinite alternate;
            stroke-width: 2;
            stroke: #365FA0;
            font-size: 50px;
        }

        @keyframes stroke {
            0% {
                fill: rgba(72,138,204,0);
                stroke: rgba(54,95,160,1);
                stroke-dashoffset: 25%;
                stroke-dasharray: 0 50%;
                stroke-width: 2;
            }

            70% {
                fill: rgba(72,138,204,0);
                stroke: rgba(54,95,160,1);
            }

            80% {
                fill: rgba(72,138,204,0);
                stroke: rgba(54,95,160,1);
                stroke-width: 3;
            }

            100% {
                fill: rgba(72,138,204,1);
                stroke: rgba(54,95,160,0);
                stroke-dashoffset: -25%;
                stroke-dasharray: 50% 0;
                stroke-width: 0;
            }
        }

        .wrapper {
            background-color: #FFFFFF;
        };

        #chapter-list {
            list-style-type: none;
            padding: 0;
        }

        .chapter-item {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
        }

        .chapter-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 5px;
        }

        .chapter-content {
            white-space: pre-wrap;
        }

        #chapter-display {
            margin-top: 50px;
            margin-bottom: 50px;
            padding: 30px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0px 5px 13px 0px rgba(8, 5, 5, 0.09);
        }

        #chapter-display h2 {
            color: #2c3e50;
        }

        .error {
            color: #e74c3c;
            font-weight: bold;
        }

        .button-container {
            position: fixed;
            bottom: 0;
            width: 1280px;
            background-color: #fff;
            padding: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 5px;
            box-shadow: 0px -3px 14px -3px rgba(8, 5, 5, 0.28);
        }

        button {
            padding: 10px 15px;
            margin: 0 5px;
            border: none;
            border-radius: 5px;
            background-color: #2980b9;
            color: #fff;
            cursor: pointer;
        }

        button:hover {
            background-color: #1c598a;
        }

        .empty-space {
            width: 80px;
            ;
        }

        #popup {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 10;
        }

        .popup-content {
            background-color: #fff;
            padding: 20px;
            width: 80%;
            max-width: 600px;
            border-radius: 10px;
            position: relative;
        }

        .close-button {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 1.5em;
            cursor: pointer;
            color: #e74c3c;
        }

        #chapter-list {
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
'''
    script = '''
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            let chaptersData;
            let currentIndex = 0;

            try {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', 'chapters_content.json', false);
                xhr.send(null);
                
                if (xhr.status === 200) {
                    chaptersData = JSON.parse(xhr.responseText);
                } else {
                    throw new Error('Failed to load chapters_content.json');
                }
            } catch (error) {
                console.error('Error loading chapters:', error);
                document.body.innerHTML += `<p class="error">Error loading chapters: ${error.message}. Please make sure chapters_content.json is in the same directory as this HTML file and the JSON is valid.</p>`;
                return;
            }

            const chapters = chaptersData;
            const chapterList = document.getElementById('chapter-list');
            const chapterDisplay = document.getElementById('chapter-display');
            const prevPlaceholder = document.getElementById('prev-placeholder');
            const nextPlaceholder = document.getElementById('next-placeholder');
            const listButton = document.getElementById('list-button');
            const popup = document.getElementById('popup');
            const closeButton = document.querySelector('.close-button');

            function displayChapter(index) {
                const chapter = chapters[index];
                if (chapter) {
                    chapterDisplay.innerHTML = `
                        <h2>${chapter.title}</h2>
                        <div class="chapter-content">${chapter.content}</div>
                    `;
                    window.scrollTo(0, 0);
                }
                updateButtons(index);
            }

            function displayChapter(index) {
                const chapter = chapters[index];
                if (chapter) {
                    chapterDisplay.innerHTML = `
                        <h2>${chapter.title}</h2>
                        <div class="chapter-content">${chapter.content}</div>
                    `;
                    window.scrollTo(0, 0);
                }
                updateButtons(index);
            }

            function updateButtons(index) {
                if (index === 0) {
                    prevPlaceholder.innerHTML = '';
                } else {
                    prevPlaceholder.innerHTML = '<button id="prev-button">Prev</button>';
                    const prevButton = document.getElementById('prev-button');
                    prevButton.addEventListener('click', () => {
                        if (currentIndex > 0) {
                            currentIndex--;
                            displayChapter(currentIndex);
                        }
                    });
                }

                if (index === chapters.length - 1) {
                    nextPlaceholder.innerHTML = '';
                } else {
                    nextPlaceholder.innerHTML = '<button id="next-button">Next</button>';
                    const nextButton = document.getElementById('next-button');
                    nextButton.addEventListener('click', () => {
                        if (currentIndex < chapters.length - 1) {
                            currentIndex++;
                            displayChapter(currentIndex);
                        }
                    });
                }
            }

            displayChapter(currentIndex);

            listButton.addEventListener('click', () => {
                chapterList.innerHTML = '';
                chapters.forEach((chapter, index) => {
                    const li = document.createElement('li');
                    li.className = 'chapter-item';
                    li.innerHTML = `<div class="chapter-title">${chapter.title}</div>`;
                    li.addEventListener('click', () => {
                        currentIndex = index;
                        displayChapter(currentIndex);
                        popup.style.display = 'none';
                    });
                    chapterList.appendChild(li);
                });
                popup.style.display = 'flex';
            });

            closeButton.addEventListener('click', () => {
                popup.style.display = 'none';
            });

            window.addEventListener('click', (e) => {
                if (e.target === popup) {
                    popup.style.display = 'none';
                }
            });
        });
    </script>
'''
    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story_title}</title>
    {style}
</head>
<body>
    <div class="wrapper">
        <svg>
            <text x="50%" y="50%" dy=".35em" text-anchor="middle">
                {story_title}
            </text>
        </svg>
    </div>
    
    <div id="chapter-display"></div>
    
    <!-- Popup -->
    <div id="popup">
        <div class="popup-content">
            <span class="close-button">X</span>
            <ul id="chapter-list"></ul>
        </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="button-container">
        <div id="prev-placeholder" class="empty-space"></div>
        <button id="list-button">List Chapters</button>
        <div id="next-placeholder" class="empty-space"></div>
    </div>

    {script}
</body>
</html>
'''
    return html

def create_readme(folder_name):
    readme_file = os.path.join(folder_name, "readme.md")

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f'''
Run Terminal:
```bash
    python -m http.server 8000
```
Open Browser:
```bash
    http://localhost:8000/{folder_name}/chapter_viewer.html
```
''')

def setup_logging(folder_name):
    log_file = os.path.join(folder_name, 'log.txt')
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def get_story_title(browser, url):
    browser.get(url)
    try:
        title_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[1]/div[1]/div[2]/h1/a"))
        )
        return title_element.text
    except Exception as e:
        logging.error(f"Error extracting story title: {str(e)}")
        return "Untitled Story"

def login(browser, base_url):
    logging.info("Starting login process")
    browser.get(base_url)
    sleep(3)

    try:
        # Click on the menu button
        menu_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/header/div/div/div[3]/button'))
        )
        menu_button.click()

        # Click on the login button
        login_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[1]/button'))
        )
        login_button.click()

        # Enter email
        email_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[1]/div[2]/input'))
        )
        email_input.send_keys(EMAIL)  # Replace with actual email

        # Enter password
        password_input = browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/input')
        password_input.send_keys(PASSWORD)  # Replace with actual password

        # Click login button
        submit_button = browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[3]/div[1]/button')
        submit_button.click()

        # Wait for login to complete
        sleep(5)
        logging.info("Login process completed")

    except Exception as e:
        logging.error(f"An error occurred during login: {str(e)}")

def extract_chapter_links(url, folder_name, browser):
    json_file_path = os.path.join(folder_name, "chapter_links.json")

    try:
        browser.get(url)
        sleep(3)

        buttonOpenMenu = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div[1]/div[1]/div[2]/div[2]/button[2]'))
        )
        buttonOpenMenu.click()

        links = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@data-x-bind="ChapterItem(index)"]'))
        )
        logging.info(f"Found {len(links)} chapter links")

        href_list = [link.get_attribute("href") for link in links]

        with open(json_file_path, 'r+', encoding='utf-8') as json_file:
            existing_links = json.load(json_file)
            existing_links.extend(href_list)
            json_file.seek(0)
            json.dump(list(set(existing_links)), json_file, ensure_ascii=False, indent=2)
            json_file.truncate()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return href_list

def crawl_chapters(folder_name, chapter_links, browser):
    logging.info(f"Crawl script started at {datetime.now()}")

    output_file_path = os.path.join(folder_name, "chapters_content.json")

    try:
        with open(output_file_path, 'r', encoding='utf-8') as input_file:
            chapters_data = json.load(input_file)
    except (json.JSONDecodeError, FileNotFoundError):
        chapters_data = []

    existing_chapter_ids = set(chapter['id'] for chapter in chapters_data)

    try:
        for index, link in enumerate(chapter_links, start=1):
            chapter_id = f"chapter-{index}"
            
            if chapter_id in existing_chapter_ids:
                logging.info(f"Chapter {index} already exists. Skipping.")
                continue

            start_time = time()
            browser.get(link)
            
            try:
                content_element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "chapter-detail"))
                )
                chapter_content = content_element.text

                title_element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='app']/main/div[2]/div/h2"))
                )
                chapter_title = title_element.text

                chapter_data = {
                    "id": chapter_id,
                    "title": chapter_title,
                    "content": chapter_content
                }

                chapters_data.append(chapter_data)
                existing_chapter_ids.add(chapter_id)

                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(chapters_data, output_file, ensure_ascii=False, indent=2)

                end_time = time()
                crawl_time = end_time - start_time
                logging.info(f"[{index}/{len(chapter_links)}] Successfully crawled and saved chapter: {chapter_title}. Time taken: {crawl_time:.2f} seconds")
            except Exception as e:
                logging.error(f"Error crawling chapter {index}: {str(e)}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    logging.info(f"Crawl script completed at {datetime.now()}")

def main():
    url = input("Enter your URL: ")
    folder_name = create_folder_from_url(url)
    
    # Set up logging as soon as the folder is created
    setup_logging(folder_name)

    firefox_options = Options()
    firefox_options.add_argument("--headless")
    
    # Add these options to improve performance
    firefox_options.add_argument("--disable-extensions")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Firefox(options=firefox_options)
    logging.info("Browser initialized")

    try:
        base_url = extract_base_url(url)
        login(browser, base_url)
        story_title = get_story_title(browser, url)
        create_json_files(folder_name)
        create_chapter_viewer_html(folder_name, story_title)
        create_readme(folder_name)
        chapter_links = extract_chapter_links(url, folder_name, browser)
        crawl_chapters(folder_name, chapter_links, browser)
    except Exception as e:
        logging.error(f"An error occurred in main execution: {str(e)}")
    finally:
        browser.quit()
        logging.info("Browser closed")
        logging.info(f"Script completed at {datetime.now()}")

if __name__ == "__main__":
    main()
