
import argparse
import requests
import validators
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, RequestException
from pathlib import Path
from urllib.parse import urljoin, urlparse

def main():
    parser = argparse.ArgumentParser(description="The spider program allow you to extract all the images(jpg/jpeg; .png; .gif; .bmp) from a website, recursively, by providing a url as a parameter")

    parser.add_argument('url', type=str, help="The target website")
    parser.add_argument('-r', '--recursive', action='store_true', help="Recursively downloads the images")
    parser.add_argument('-l', '--level', type=int, default=5, help="Indicates the maximum depth level of the recursive download (default: 5)")
    parser.add_argument('-p', '--path', type=str, default="./data/", help="Indicates the path where the downloaded files will be saved (default: ./data/)")

    # Récupérer les arguments saisis dans le terminal
    args = parser.parse_args()

    url = args.url
    url = url.split('?')[0].rstrip('/')
    url = url.split("#")[0].rstrip('/')
    recursively = args.level if args.recursive else 0
    if not validators.url(url):
        print ("Error while accessing the page: \"" + url + "\"")
        exit (1)
    domain = urlparse(url).netloc
    # print("Debug: get_image on " + url)
    get_images(url, domain, args.path, recursively, urls_downloaded = {})


def get_images(url, domain, path, recursively, urls_downloaded):
    # print()
    # print("** Debug: start rec = " + str(recursively) + " **")

    urls_downloaded[url] = False;
    # print("* Debug: url added to array = " + url + " *")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() 
    except Timeout:
        print("Erreur : La requête a expiré (Timeout).")
        return urls_downloaded
    except RequestException as e:
        print("Une erreur réseau est survenue.")
        return urls_downloaded

    html_content = BeautifulSoup(response.text, 'html.parser')
    if (url not in urls_downloaded):
        parse_download_images(html_content, url, path)


    if recursively > 0:
        recursively -= 1
        for a in html_content.find_all("a", href=True):
            href = a["href"]
            joined_link = urljoin(url, href)
            clean_link = joined_link.split("#")[0].rstrip('/')
            clean_link = clean_link.split('?')[0].rstrip('/')
            if (urls_downloaded.get(clean_link, True) not True) and (urlparse(clean_link).netloc == domain):
                # print("\n------ Debug: Recursive = " + str(recursively) + " url " + clean_link + " ------")
                get_images(clean_link, domain, path, recursively, urls_downloaded)
        urls_downloaded[url] = True
    return urls_downloaded


def parse_download_images(html_content, url, path):
    authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]
    
    for img in html_content.find_all('img'):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        absolute_src = urljoin(url, src)
        filename = absolute_src.rpartition('/')[-1]
        file_extension = filename.rpartition('.')[-1].lower()
        
        if file_extension in authorised_extension:
            Path(path).mkdir(parents=True, exist_ok=True)
            r = requests.get(absolute_src, allow_redirects=True)
            if r.status_code != 200:
                print ("Error while downloading the image: " + absolute_src)
                continue
            print("Downloading: " + filename + " in " + path)
            open(path + filename, 'wb').write(r.content)

if __name__ == '__main__':
    main()


    # http://0.0.0.0:8000/ == http://0.0.0.0:8000/index.html
    # mais pas pour le programme

    # index.html?x=1 pas gerer par 
    # filename = absolute_src.rpartition('/')[-1].split('?')[0]

    # la condition devrais etre si l'adresse et ses sous adresses ont ete faite ne pas y aller
    # pour cela tableau a double entree adresse - sous adresse bool
    # sous adresse seta true au moment e leur recherche. 