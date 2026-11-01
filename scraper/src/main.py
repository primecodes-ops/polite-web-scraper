import requests

URL = "https://books.toscrape.com/robots.txt"


def request():
    try:
        r = requests.get(URL)
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Could not reach site: {e}"

    if r.status_code == 404:
        print("no robots file found")
        return "no robots file found"


if __name__ == "__main__":
    request()
