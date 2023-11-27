from datetime import datetime
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class Solution:
    link: str
    code: str


def save_code(client, temp):
    resp = client.get(temp.link).text
    html = HTMLParser(resp)
    csrf_token = html.css("head meta[name=csrf-token]")[0].attributes.get("content")

    headers = {
        "X-CSRF-TOKEN": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
    }
    body = {
        "code": temp.code,
        "status": "SAVE"
    }

    response = client.post(
        temp.link.replace("start-lab", "save-code"),
        data=body, headers=headers)

    print(response.json())


def get_url(client):
    response = client.get("https://litcoder.in/candidate/labs").text
    html = HTMLParser(response)
    module_page = html.css("div.owl-carousel.owl-theme")[2].css("a.button-design.continue.items-center")
    url_list = []

    result = []

    for url in module_page:
        data = HTMLParser(client.get(url.attributes.get("href")).text).css("div.lab-practice-detail div.excerciseCard")
        for _ in data:
            url_list.append(urljoin(f'{url.attributes.get("href")}/exercises',
                                    f'{_.attributes.get("data-excercise-id")}/start-lab'))

    for url in url_list:
        data = HTMLParser(client.get(url).text).css("div#editor")[0]
        result.append(Solution(
            link=url,
            code=data.text()
        ))

    return result


def login(client, email, password):
    response = client.get("https://litcoder.in/login").content
    html = HTMLParser(response)
    token = html.css(
        "#kt_app_content_container > div > div > div.col-md-5.left-container > div > div > form > input[type=hidden]")[
        0].attributes.get("value")

    data = {
        "_token": token,
        "email": email,
        "password": password,
    }

    client.post("https://litcoder.in/login", data=data, follow_redirects=True)


def run():
    client = httpx.Client()
    login(client, "Account credentials of a user who has already completed the Litcoder lab. (university email)", "password")

    data = get_url(client)
    newClient = httpx.Client()
    login(newClient, "Account credentials of a user to whom you want to copy the lab code. (university email)", "password")
    for temp in data:
        save_code(newClient, temp)


def main():
    run()


if __name__ == "__main__":
    main()
