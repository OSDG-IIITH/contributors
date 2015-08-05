import json
import requests
import simplejson
import sys
import argparse

filters = ['easy', 'medium', 'hard', 'bug']
stats = ['additions', 'deletions', 'commits']
scoring = dict(zip(filters + stats, [20, 50, 100, 10] + [1, 1, 1]))
users = {}

parser = argparse.ArgumentParser()
parser.add_argument("token", help="Git Authorisation token")
args = parser.parse_args()
token = args.token  # Authorisation token passed as an argument


def init_user(login):
    users[login] = dict(zip(filters + stats, len(filters + stats) * [0]))


def req(get, params={}):
    """Function to send HTTP Requests"""
    params['access_token'] = token
    api_host = "https://api.github.com"
    url = api_host + get
    resp = requests.get(url=url, params=params)

    try:
        data = json.loads(resp.text)
    except:
        data = []
    return data


def get_repos(org):
    """Returns Repos under an organization"""
    url = '/orgs/' + org + '/repos'
    repo_list = req(url)
    repos = []
    for repo in repo_list:
        repos.append(repo["name"])
    return repos


def get_repo_issues(repo, org, closed=True):
    """Returns a list of issues(closed issues, by default) under a repository"""
    url = '/repos/' + org + '/' + repo + '/issues'
    params = {'state': 'closed'} if closed else {}
    issues = req(url, params)
    return issues


def filter_issues(issue_list):
    """Returns a list of issues which have specific labels"""
    filt_issues = []
    for issue in issue_list:
        labels = issue['labels']
        for label in labels:
            lname = label['name'].lower()
            if lname in filters:
                filt_issues.append(issue)

    return filt_issues


def update_issue_count(issue_list):
    """Updates issue count for every contributor"""
    for issue in issue_list:
        if(issue['assignee']):
            assignee = issue['assignee']['login']
            if not users.has_key(assignee):
                init_user(assignee)
        else:
            # no points if no assignee
            continue
        labels = issue['labels']
        for label in labels:
            lname = label['name'].lower()
            if(lname in filters):
                users[assignee][lname] += 1


def score(user):
    """Returns a total for a user based on counts"""
    ans = 0

    for lbl, ct in users[user].iteritems():
        users[user][lbl] = scoring[lbl] * ct

    return ans


def update_contributors(repo, org):
    """Updates list of contributors with additions deletions, and commit counts"""
    url = '/repos/' + org + '/' + repo + '/stats/contributors'
    contribs = req(url)
    for contrib in contribs:
        login = contrib['author']['login']
        if not users.has_key(login):
            init_user(login)
        for week in contrib['weeks']:
            users[login]['additions'] += week['a']
            users[login]['deletions'] += week['d']
            users[login]['commits'] += week['c']


if __name__ == "__main__":
    org = "OSDG-IIITH"
    filename = "ranking.json"
    repos = get_repos(org)
    for repo in repos:
        update_contributors(repo, org)
        issues = get_repo_issues(repo, org)
        issues = filter_issues(issues)
        update_issue_count(issues)

    for user in users.iterkeys():
        total = score(user)
        users[user]['total'] = total

    users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    for i in range(len(users)):
        users[i] = {'user': users[i][0], 'scores': users[i][1]}

    try:
        jsonFile = open(filename, "w+")
    except IOError:
        print "Error: File cannot be opened."
    else:
        jsonFile.write(json.dumps(users))
