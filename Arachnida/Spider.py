import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def main():
    # Initialiser le dictionnaire d'arguments
    parser = argparse.ArgumentParser(description="The spider program allow you to extract all the images(jpg/jpeg; .png; .gif; .bmp) from a website, recursively, by providing a url as a parameter")

    parser.add_argument('url', type=str, help="The target website")

    parser.add_argument('-r', '--recursive', action='store_true', help="Recursively downloads the images")

    parser.add_argument('-l', '--level', type=int, default=5, help="Indicates the maximum depth level of the recursive download (default: 5)")

    parser.add_argument('-p', '--path', type=str, default="./data/", help="Indicates the path where the downloaded files will be saved (default: ./data/)")

    # Récupérer les arguments saisis dans le terminal
    args = parser.parse_args()

    if args.url != False:
        authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]
        response = requests.get(args.url)
        if response.status_code != 200:
            print ("Error while accessing the website!")
        html_content = BeautifulSoup(response.text, 'html.parser')
        get_images(html_content, authorised_extension, args)
        if args.recursive:
            for i in range(0, args.level):
                continue
                # get all the pages 
                

def get_images(html_content, authorised_extension, args):
    for img in html_content.find_all('img'):
        src = img.get("src")
        if (src == None):
            src = img.get("data-src")
        # print(src)
        filename = src.rpartition('/')[-1]
        # print(filename)
        file_extension = filename.rpartition('.')[-1]
        # print(file_extension)
        if (file_extension in authorised_extension):
            print("Downloading: " + filename + " in " + args.path)
            Path(args.path).mkdir(parents=True, exist_ok=True)
            r = requests.get(src, allow_redirects=True)
            open(args.path+filename, 'wb').write(r.content)

if __name__ == '__main__':
    main()