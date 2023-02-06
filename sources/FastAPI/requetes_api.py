import requests
from pprint import pprint
#from bs4 import BeautifulSoup
import json as js

API_URL = "http://localhost:8000" 

def request_get(route, auth_code):
    response = requests.get(
        url=f"{API_URL}/"+route,
        headers={
            "Authorization" : "Basic "+auth_code
        }
    )

    #print(response.status_code)
    #pprint(response.headers)

    #soup = BeautifulSoup(response.text, features="lxml")
    #print(soup.get_text())
    return response.status_code

def request_post(route, auth_code, data_dict):
    response = requests.post(
        url=f"{API_URL}/"+route,
        headers={
            "Authorization" : "Basic "+auth_code
        },
        data=js.dumps(data_dict),
    )

    print(response.status_code)
    pprint(response.headers)

    #soup = BeautifulSoup(response.text, features="lxml")
    #print(soup.get_text())
    return (response.status_code,response.text)

def request_delete(route, auth_code):
    response = requests.delete(
        url=f"{API_URL}/"+route,
        headers={
            "Authorization" : "Basic "+auth_code
        }
    )

    print(response.status_code)
    pprint(response.headers)

    #soup = BeautifulSoup(response.text, features="lxml")
    #print(soup.get_text())
    return response.status_code
