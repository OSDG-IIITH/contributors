import user as USER ,sqlite3
conn = sqlite3.connect("data.db")

cursor = conn.cursor()

cursor.execute(''' CREATE TABLE IF NOT EXISTS userdata
                   (name text, repo text, contribution real)''')

username=raw_input()
password=raw_input()
user    =raw_input()

USER.getdata(username,password,user,cursor)

for row in cursor.execute("SELECT * FROM userdata"):
    print row

