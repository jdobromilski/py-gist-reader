"""
gist_reader.py: Read gists for a given user
"""
import datetime
import json
import os

import click
from github import Github, GithubException, GithubObject

STATE_FILE = "last_run.json"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
GITHUB_CLIENT = None


@click.group()
@click.option('--auth-token', '-t', 'auth_token', required=False,
              default=lambda: os.environ.get("GISTS_AUTH_TOKEN", None),
              help="Authentication token, gets environment variable GISTS_AUTH_TOKEN")
def cli(auth_token):
    """Read user gists"""
    global GITHUB_CLIENT

    GITHUB_CLIENT = Github(auth_token)


@cli.command('get')
@click.option('--user', '-u', 'user', required=True,
              help="Specify GitHub username with public gists")
@click.option('--since-last-run', '-r', 'since_last_run', is_flag=True, show_default=False,
              required=False, default=False, help="Lists gists created since last local execution")
@click.option('--since-given-datetime', '-s', 'since_given_datetime', required=False, default=None,
              help="Warning! Ignored if --since-last-run flag is 'True'. List of gists published " +
              "since given datetime, (Format: '2022-09-26T14:54:54Z')")
def get(user, since_last_run, since_given_datetime):
    """Gists for given user"""
    user_gists = get_gists(user, since_last_run, since_given_datetime)

    print(f"Number of gists for {user}: {len(user_gists)}")
    for gist in user_gists:
        print(
            f"Id: {gist.id}, Date created: {gist.created_at}, Description: {gist.description}")


def get_gists(user, since_last_run, since_given_datetime):
    """Read user gists"""
    # User: jdobromilski

    user_gists = []
    page = 0

    if since_last_run is True:
        since_when = read_last_execution_time(user)
    elif since_given_datetime is not None:
        since_when = datetime.datetime.strptime(
            since_given_datetime, DATETIME_FORMAT)
    else:
        since_when = GithubObject.NotSet

    while True:
        try:
            resp = GITHUB_CLIENT.get_user(
                user).get_gists(since_when).get_page(page)
        except GithubException as exc:
            raise exc

        if resp != []:
            user_gists += resp
            page += 1
        else:
            break

    write_current_execution_time(user)

    return user_gists


def write_current_execution_time(user):
    """Save latest execution details"""
    data = {}
    current_datetime = datetime.datetime.now().strftime(DATETIME_FORMAT)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

    data[user] = current_datetime

    with open(STATE_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_last_execution_time(user):
    """Read latest execution details"""
    data = {}

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())[user]

    data = datetime.datetime.strptime(data, DATETIME_FORMAT)

    return data


def gist_details():
    """Get gist details"""


if __name__ == '__main__':
    cli()
