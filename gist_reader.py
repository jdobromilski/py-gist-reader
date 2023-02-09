"""
gist_reader.py: Read gists for a given user
"""
import datetime
import json
import os

import click
from github import Github, GithubException, GithubObject

state_file = "last_run.json"
datetime_format = "%Y-%m-%dT%H:%M:%SZ"


@click.group()
@click.option('--user', '-u', 'user', required=True,
              help="Specify GitHub username with public gists")
@click.option('--since-last-run', '-r', 'since_last_run', is_flag=True, show_default=False,
              required=False, default=False, help="Lists gists created since last local execution")
@click.option('--since-given-datetime', '-s', 'since_given_datetime', required=False,
              help="Warning! Ignored if --since-last-run flag is 'True'. List of gists published since " +
              "given datetime, (Format: '2022-09-26T14:54:54Z')")
@click.pass_context
def cli(ctx, user, since_last_run, since_given_datetime):
    """Read user gists"""
    ctx.ensure_object(dict)
    ctx.obj['USER'] = user
    ctx.obj['SINCE_GIVEN_DATETIME'] = since_given_datetime
    ctx.obj['SINCE_LAST_RUN'] = since_last_run


@cli.command('list')
@click.pass_context
def list(ctx):
    """Gists for given user"""
    user_gists = get_gists(
        ctx.obj['USER'], ctx.obj['SINCE_LAST_RUN'], ctx.obj['SINCE_GIVEN_DATETIME'])

    print(f"Number of gists for {ctx.obj['USER']}: {len(user_gists)}")
    for gist in user_gists:
        print(
            f"Id: {gist.id}, Date created: {gist.created_at}, Description: {gist.description}")


def get_gists(user, since_last_run, since_given_datetime):
    """Read user gists"""
    # User: JoeyBurzynski
    github_client = Github()
    user_gists = []
    page = 0

    if since_last_run == True:
        last_run = read_last_execution_time(user)
        print(f"Last execution time: {last_run}")
    else:
        last_run = GithubObject.NotSet

    while True:
        try:
            resp = github_client.get_user(
                user).get_gists(last_run).get_page(page)
        except GithubException as e:
            raise Exception(1, f"Error pulling gists: {e.data['message']}")

        if resp != []:
            user_gists += resp
            page += 1
        else:
            break

    write_current_execution_time(user)

    return user_gists


def write_current_execution_time(user):
    """Save latest execution details"""
    # global state_file
    data = {}
    current_datetime = datetime.datetime.now().strftime(datetime_format)

    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

    data[user] = current_datetime

    with open(state_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_last_execution_time(user):
    """Read latest execution details"""
    data = {}

    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())[user]

    data = datetime.datetime.strptime(data, datetime_format)

    return data


def gist_details():
    """Get gist details"""


if __name__ == '__main__':
    cli()
