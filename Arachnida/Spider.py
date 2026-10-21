import argparse
import requests
import validators
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse

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
        url = args.url
        recursively = 0
        if args.recursive:
            recursively = args.level
        if not validators.url(url):
            print ("Error while accessing the page: \"" + url + "\"")
            exit (1)
        domain = urlparse(url).netloc
        base_url = "https://" + domain
        # print ("Debug: " + domaine)
        # print ("Debug: " + base_url)
        get_images(url, domain, base_url, args, recursively)


def get_images(url, domain, base_url, args, recursively):
    authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]
    response = requests.get(url)
    if response.status_code != 200:
        print ("Error while accessing the page: " + url)
        exit (1)
    
    html_content = BeautifulSoup(response.text, 'html.parser')


    for img in html_content.find_all('img'):
        src = img.get("src")
        if (src == None):
            src = img.get("data-src")
        # print("Debug: " + src)
        filename = src.rpartition('/')[-1]
        # print("Debug: " + filename)
        file_extension = filename.rpartition('.')[-1]
        # print("Debug: " + file_extension)
        
        if file_extension in authorised_extension:
            print("Downloading: " + filename + " in " + args.path)
            Path(args.path).mkdir(parents=True, exist_ok=True)
            r = requests.get(src, allow_redirects=True)
            open(args.path+filename, 'wb').write(r.content)
    if recursively > 0:
        recursively -= 1
        print("------ Debug: Recursive = " + str(recursively) + " ------")
        for b in html_content.find_all("a", href=True):
            href = b["href"]
            # managing the relative link -> absolute link
            joined_link = urljoin(base_url, href)
            # remove the # section at the end of the link
            clean_link = joined_link.split("#")[0]
            # check that the link stay on the same website
            if clean_link != url and urlparse(clean_link).netloc == domain:
                print("Debug: " + clean_link)
                get_images(clean_link, domain, base_url, args, recursively)

if __name__ == '__main__':
    main()