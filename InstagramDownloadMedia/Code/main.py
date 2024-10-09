import os
import subprocess
import concurrent.futures

def delete_non_media_files(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and not filename.endswith('.jpg') and not filename.endswith('.mp4'):
            os.remove(filepath)

def download_instagram_account(username):
    print(f"Downloading files from username: {username}")
    subprocess.run(["python", "-m", "instaloader", username])
    delete_non_media_files(username)
    print(f"Finished downloading and processing {username}")

def main():
    print("Enter Instagram usernames (one per line). Press Enter twice when done:")
    usernames = []
    while True:
        username = input("Enter your Instagram username: ")
        if username == "":
            break
        usernames.append(username)
        print("Downloading file from username:", username)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_instagram_account, usernames)

    print("All downloads completed.")

main()