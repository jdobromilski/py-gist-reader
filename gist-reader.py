"""
gist-reader.py: Reads gist for given user
"""

from multiprocessing import context
import click
from github import Github

github_client = None
github_user = None

@click.group()
@click.option('--user', '-u', 'user', required=True,
    help="GitHub username whose gists will be listed (Username:<name>)")
def cli(user):
    """List available gists"""
    global github_client
    global github_user

    github_client = Github()
    github_user = user
    
@cli.command()
def list():
    """list User gists"""
    print(context)
    user = "JoeyBurzynski"
    user_gists = get_gists(github_user)

    print(f"Number of gists for %s: %i", user, len(user_gists))
    for gist in user_gists:
        print(gist)

def get_gists(user):
    """Read user gists"""
    user_gists = []
    page = 0

    while True:
        resp = github_client.get_user(user).get_gists().get_page(page)
        if resp != []:
            user_gists += resp
            page += 1
        else:
            print("Full list of gists.")
            break
    
    return user_gists

if __name__ == '__main__':
    cli()
