import hashlib
import argparse
import requests
import validators
import os
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, RequestException
from pathlib import Path
from urllib.parse import urljoin, urlparse

hashes_contents = set()
links_cache = {}

def main():
    parser = argparse.ArgumentParser(description="The spider program allow you to extract all the images(jpg/jpeg; .png; .gif; .bmp) from a website, recursively, by providing a url as a parameter")

    parser.add_argument('url', type=str, help="The target website")
    parser.add_argument('-r', '--recursive', action='store_true', help="Recursively downloads the images")
    parser.add_argument('-l', '--level', type=int, default=5, help="Indicates the maximum depth level of the recursive download (default: 5)")
    parser.add_argument('-p', '--path', type=str, default="./data/", help="Indicates the path where the downloaded files will be saved (default: ./data/)")

    args = parser.parse_args()

    url = args.url
    url = url.split('?')[0].rstrip('/')
    url = url.split("#")[0].rstrip('/')
    recursively = args.level if args.recursive else 0
    if not validators.url(url):
        print (f"Error while accessing the page: \"{url}\"")
        exit (1)
    domain = urlparse(url).netloc
    if not os.path.isdir(args.path):
        try:
            Path(args.path).mkdir(parents=True, exist_ok=True)
        except Exception:
            print(f"Error cant create directory: {args.path}")
            exit(1)
    if not os.access(args.path, os.W_OK):
        print(f"Error permission denied on: {args.path}")
        exit (1)
    visited_urls = {}
    parse_url_recursivelly(url, domain, args.path, recursively, visited_urls)


def parse_url_recursivelly(url, domain, path, depth, visited_urls):
    
    if url in visited_urls and (visited_urls[url] >= depth or visited_urls[url] == -1):
        return

    if url in links_cache:
        links = links_cache[url]
    else:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except (Timeout, RequestException):
            visited_urls[url] = -1
            return

        if "text/html" not in response.headers.get("Content-Type", ""):
            visited_urls[url] = -1
            return

        html_content = BeautifulSoup(response.text, 'html.parser')
        if not is_already_downloaded_page(response.text):
            download_images(html_content, url, path)

        links = []
        for a in html_content.find_all("a", href=True):
            joined_link = urljoin(url, a["href"])
            links.append(joined_link.split("#")[0].split('?')[0].rstrip('/'))
        links_cache[url] = links

    visited_urls[url] = depth

    if depth > 0:
        for clean_link in links:
            if urlparse(clean_link).netloc == domain:
                parse_url_recursivelly(clean_link, domain, path, depth - 1, visited_urls)


def download_images(html_content, url, path):
    authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]

    print(f"Page: {url}")

    for img in html_content.find_all('img'):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        absolute_src = urljoin(url, src)
        filename = absolute_src.rpartition('/')[-1]
        file_extension = filename.rpartition('.')[-1].lower()

        if file_extension in authorised_extension:
            try:
                r = requests.get(absolute_src, allow_redirects=True)
            except (Timeout, RequestException) as e:
                print (f"Error while downloading the image: {absolute_src}")
                continue
            print(f"Downloading: {filename}")
            open(path + '/' + filename, 'wb').write(r.content)
    print()


def is_already_downloaded_page(html_content):
    cleaned_content = html_content.strip()
    hash_page = hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()
    
    if hash_page in hashes_contents:
        return True
    else:
        hashes_contents.add(hash_page)
        return False

if __name__ == '__main__':
    main()