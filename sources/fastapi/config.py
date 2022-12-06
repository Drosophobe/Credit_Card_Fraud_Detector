# Config file

# Path definition to acces to the csv file
path = 'Datasets/'

# User database with name & password
'''
{
  "patrick": "moorea",
  "pierre": "BrochetSilure26",
  "admin": "admin" 
}
'''
import json

f = open(path+'users.json', 'r')
users_db = json.load(f)
f.close()



