import json, requests
import simplejson
import json

filters=['easy','medium','hard','bug']
scoring=dict(zip(filters,[20,50,100,10]))
users={}
def req(get,params={}):
    """Function to send HTTP Requests"""
    params['access_token']='da7992131c669b19e38da47fadf63e080174ffb7'
    api_host="https://api.github.com"
    url=api_host+get
    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    return data


def get_repos(org):
    """Returns Repos under an organization"""
    url='/orgs/'+org+'/repos'
    repo_list=req(url)

    repos=[]
    for repo in repo_list:
        repos.append(repo["name"])

    return  repos

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

def update_count(issue_list):
    for issue in issue_list:
        if(issue['assignee']):
            assignee=issue['assignee']['login']
            if not users.has_key(assignee):
               users[assignee]=dict(zip(filters,len(filters)*[0]))
        else:
            #no points if no assignee
            continue
        labels=issue['labels']
        for label in labels:
            lname=label['name'].lower()
            if(lname in filters):
                users[assignee][lname]+=1


def score(lblct):

    #defaut score is 10
    ans=10


    for lbl,ct in lblct.iteritems():
            ans+=scoring[lbl]*ct

    return ans



if __name__ == "__main__":
    org="OSDG-test"
    filename="ranking.json"
    repos=get_repos(org)
    for repo in repos:
        issues=get_repo_issues(repo,org)
        issues=filter_issues(issues)
        update_count(issues)

    for user in users.iterkeys():
        total=score(users[user])
        users[user][total]=total

    with open(filename, "w") as jsonFile:
            jsonFile.write(json.dumps(users))
