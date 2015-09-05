from github import Github
import requests
import json
import sqlite3

#User=raw_input()
#password=raw_input()
#user=raw_input()

def getdata(username,password,user,conn):
    cursor=conn.cursor()
    g=Github(username,password)
    Name=g.get_user(user).name

    for repo in g.get_user(user).get_repos():
        owner=""

        #GET THE OWNER OF THE REPO IN CASE IT IS FORKED
        if repo.parent:
            owner=repo.parent.owner.login
        else: 
            owner=repo.owner.login

        #GET THE JSON OF STATS CONTRIBUTOR IN THAT REPO
        url="https://api.github.com/repos/"+owner+"/"+repo.name+"/stats/contributors"
        print url
        r=requests.get(url)
        repoItem=json.loads(r.text or r.content)

        #GET TOTAL NUMBER OF LINES IN THE REPO
        url1="https://api.github.com/repos/"+owner+"/"+repo.name+"/languages"
        print url1
        r1 = requests.get(url1)
        repoItem1 = json.loads(r1.text or r1.content)
        total=0


        for i in repoItem1:
            total += int(repoItem1[i])

        #ITERATE OVER CONTRIBUTORS IN STATS AND FIND REQUIRED USER
        for i in repoItem:
            if i["author"]["login"]!=user:
                continue
            k=0
            for j in  i["weeks"]:
                k+=int(j["a"])+int(j["c"])

            result = cursor.execute("SELECT * FROM userdata WHERE name = :name and repo = :reponame",{"name":Name, "reponame":repo.name}).fetchall()
            
            if len(result)==0:
                cursor.execute("INSERT INTO userdata VALUES (?,?,?)",(Name,repo.name,k*1.0/total*1.0))
                conn.commit()
            elif len(result)==1:
                cursor.execute("UPDATE userdata SET contribution = :cont WHERE name = :name and repo = :reponame",{"name":Name, "reponame":repo.name, "cont":k*1.0/total*1.0})
                conn.commit()

            break

