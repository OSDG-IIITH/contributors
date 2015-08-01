import json, requests
import simplejson
import json

filters=['easy','medium','hard','bug']
stats=['additions','deletions','commits']
scoring=dict(zip(filters+stats,[20,50,100,10]+[1,1,5]))
users={}
def init_user(login):
    users[login]=dict(zip(filters+stats,len(filters+stats)*[0]))

def req(get,params={}):
    """Function to send HTTP Requests"""
<<<<<<< HEAD
    params['access_token']='888d06eaeca57ad57b8ac1b0fb96d86a96d4b491'
=======
    params['access_token']=''
>>>>>>> dc03e8caabe49a8ef1592676e9b241e81e1b402f
    api_host="https://api.github.com"
    url=api_host+get
    resp = requests.get(url=url, params=params)

    try:
        data = json.loads(resp.text)
    except:
        data=[]
    return data


def get_repos(org):
    """Returns Repos under an organization"""
    url='/orgs/'+org+'/repos'
    repo_list=req(url)
    repos=[]
    for repo in repo_list:
        repos.append(repo["name"])
    return repos

def get_repo_issues(repo,org,closed=True):
    """Returns a list of issues(closed issues, by default) under a repository"""
    url='/repos/'+org+'/'+repo+'/issues'
    params={'state':'closed'} if closed else {}
    issues=req(url,params)
    return issues



def filter_issues(issue_list):
    """Returns a list of issues which have specific labels"""

    filt_issues=[]
    for issue in issue_list:
        labels=issue['labels']
        for label in labels:
            lname=label['name'].lower()
            if lname in filters:
                filt_issues.append(issue)

    return filt_issues

def update_issue_count(issue_list):
    for issue in issue_list:
        if(issue['assignee']):
            assignee=issue['assignee']['login']
            if not users.has_key(assignee):
                init_user(assignee)
        else:
            #no points if no assignee
            continue
        labels=issue['labels']
        for label in labels:
            lname=label['name'].lower()
            if(lname in filters):
                users[assignee][lname]+=1


def score(count):

    #defaut score is 10
    ans=10


    for lbl,ct in count.iteritems():
            ans+=scoring[lbl]*ct

    return ans

def update_contributors(repo,org):
    """Updates list of contributors with additions deletions, and commit counts"""
    url='/repos/'+org+'/'+repo+'/stats/contributors'
    contribs=req(url)
    for contrib in contribs:
            login=contrib['author']['login']
            if not users.has_key(login):
               init_user(login)
            for week in contrib['weeks']:
                users[login]['additions']+=week['a']
                users[login]['deletions']+=week['d']
                users[login]['commits']+=week['c']



if __name__ == "__main__":
    org="OSDG-test"
    filename="ranking.json"
    repos=get_repos(org)
    for repo in repos:
        update_contributors(repo,org)
        issues=get_repo_issues(repo,org)
        issues=filter_issues(issues)
        update_issue_count(issues)

    for user in users.iterkeys():
        total=score(users[user])
        users[user]['total']=total

    with open(filename, "w") as jsonFile:
            jsonFile.write(json.dumps(users))
