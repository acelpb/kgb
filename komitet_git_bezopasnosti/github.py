"""Github API module."""
import logging

import requests

from .config import HIDDEN
from .config import GH_TOKEN
from .config import STATUS_CONTEXT

log = logging.getLogger(__name__)


def check_url(url, start="https://api.github.com/"):
    if url.startswith(start):
        return True
    log.error({"error": "UNTRUSTED_API_URL",
               "bad_url": url})
    return False


def protect(string):
    return string.replace("[", "\[")


def quote(string):
    return ">" + string.replace("\n", "\n>")


def get_commits(url):
    if check_url(url):
        commits = requests.get(url, params={"access_token": GH_TOKEN})
        return commits.json()
    else:
        return None


def get_comments(url):
    result = []
    if check_url(url):
        comments = requests.get(url, params={"access_token": GH_TOKEN})
        for comment in comments.json():
            if comment["body"].startswith(HIDDEN):
                result.append(comment)
    return result


def delete_comment(comment):
    url = comment["url"]
    if check_url(url):
        requests.delete(comment["url"], params={"access_token": GH_TOKEN})


def upsert_comment(url, messages):
    if not check_url(url):
        return
    comments = get_comments(url)
    message = HIDDEN + "\n\n".join(messages)

    if len(messages) == 0:
        for comment in comments:
            delete_comment(comment)
    else:
        if len(comments) > 1:
            for comment in comments:
                delete_comment(comment)
            create_comment(url, message)
        if len(comments) == 1:
            if comments[0]["body"] != message:
                update_comment(comments[0], message)
        else:
            create_comment(url, message)


def update_comment(comments, body):
    if check_url(comments["url"]):
        requests.patch(comments["url"],
                       params={"access_token": GH_TOKEN},
                       json={"body": body})


def create_comment(url, body):
    if check_url(url):
        requests.post(url,
                      params={"access_token": GH_TOKEN},
                      json={"body": body})


def update_status(url, state, message):
    if check_url(url):
        requests.post(url,
                      params={"access_token": GH_TOKEN},
                      json={"state": state,
                            "context": STATUS_CONTEXT,
                            "description": message})
