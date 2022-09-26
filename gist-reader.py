"""
gist-reader.py: Reads gist for given user
"""

from multiprocessing import context
import click
import datetime
from github import Github
import json
import os

github_client = None
github_user = None
state_file = "last_run.json"

@click.group()
def cli():
    """List available gists"""
    global github_client
    github_client = Github()
    # github_user = user
    
@cli.command()
@click.option('--since-last-run', '-r', 'since_last_run', is_flag=True, show_default=True, 
    required=False, default=True, help="Lists gists created since last local execution")
@click.option('--user', '-u', 'user', required=True,
    help="Specify GitHub username with public gists")
@click.option('--since', '-s', 'since', required=False,
    help=f"Warning! Ignored if --since-last-run flag is 'True'. List of gists published since given datetime, \n" + \
    "(Format: '2022-09-26T14:54:54Z')")    

def list(user, since, since_last_run):
    """list User gists"""
    user_gists = get_gists(user, since, since_last_run)

    print(f'Number of gists for {user}: {len(user_gists)}')
    for gist in user_gists:
        print(f"Id: {gist.id}, Date created: {gist.created_at}, Description: {gist.description}")

def get_gists(user, since, since_last_run):
    """Read user gists"""
    # User: JoeyBurzynski
    user_gists = []
    page = 0
    since = datetime.datetime.strptime(since, "%Y-%m-%dT%H:%M:%SZ")

    while True:
        resp = github_client.get_user(user).get_gists(since=since).get_page(page)
        if resp != []:
            user_gists += resp
            page += 1
        else:
            print(f"Pulled list of gists since {since}")
            break
    
    write_last_run(user, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    return user_gists

def write_last_run(user, current_datetime):
    """Save latest execution details"""
    # global state_file
    data = {}

    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
    
    data[user] = current_datetime

    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_last_run(user):
    """Read latest execution details"""
    data = {}

    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            data[user] = json.loads(f.read())[user]
    
    return data

def gist_details():
    """Get gist details"""

if __name__ == '__main__':
    cli()
