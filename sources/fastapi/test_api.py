# ======================================================================
# Credit Card Fraud Detection API test programm
# v 1.0.1
# P. Sarzier, P.Hutter
# Datascientest MLOps Oct. 2022
# ======================================================================


from requetes_api import request_get, request_post, request_delete
import base64
from config import users_db

# generating codes from username & password
code=[]
for i,item in enumerate(users_db.keys()):
    code.append(base64.b64encode(bytes(item+':'+users_db.get(item), "UTF-8")).decode())


import pytest

# Test 1 / Access to welcome page
@pytest.mark.parametrize(
    "code,expected", [
    (code[0], 200), # req ok with user patrick, return status 200
    (code[1], 200), # req ok with user pierre, return status 200
    (code[2], 200), # req ok with user admin, return status 200
    ("", 200)])   # req ok with all users, return status 200
def test_requests_welcome_page(code,expected):
    assert (request_get("", code) == expected)

# Test 2 / Use of Fraud detection model
q_no_fraud={
        'distance_from_home': 1000,
        'distance_from_last_transaction': 500,
        'ratio_to_median_purchase_price': 0.5,
        'repeat_retailer': 20,
        'used_chip': 0,
        'used_pin_number': 0,
        'online_order': 1
        }

q_fraud={
        'distance_from_home': 10,
        'distance_from_last_transaction': 20,
        'ratio_to_median_purchase_price': 0.5,
        'repeat_retailer': 1,
        'used_chip': 1,
        'used_pin_number': 1,
        'online_order': 1
}

q_no_fraud2 = dict(q_no_fraud)
del q_no_fraud2['distance_from_home']

@pytest.mark.parametrize(
    "code,body,expected_status,expected_value", [
    (code[0],q_no_fraud, 200, '{"fraud ?":"Fraud"}'), # req ok with user patrick, return status 200
    (code[1],q_no_fraud, 200, '{"fraud ?":"Fraud"}'), # req ok with user pierre, return status 200
    (code[2],q_no_fraud2, 422, '{"fraud ?":"Fraud"}'),# req nok missing requiered field, return status 422
    ("",q_no_fraud, 401, '{"fraud ?":"Fraud"}'),      # req nok no authorized user, return status 401
    ('YWxpY2U6d29uZGVybGFuZA==',q_no_fraud, 401, '{"fraud ?":"Fraud"}'), # req nok no authorized user, return status 401
    (code[2],q_fraud, 200,'{"fraud ?":"No Fraud"}')   # req ok 
    ])
def test_requests_fraud_dtection(code,body,expected_status,expected_value):
    resp=request_post("users/predict",code,body)
    assert (resp[0] == expected_status)
    if resp[0]==200:
        assert (request_post("users/predict",code,body)[1] == expected_value)
    
# Test 3 / Acount management
user_1={
    'name': 'alice',
    'password': 'wonderland'
}
user_2={
    'name': 'bob',
    'password': 'builder'
}
user_3={
    'name': '',
    'password': 'builder'
}
user_4={
    'name': 'bob',
    'password': ''
}
@pytest.mark.parametrize(
    "code,body,expected", [
    (code[0],user_1, 401), # req nok with user patrick, return status 401
    (code[2],user_1, 200), # req ok with user admin, return status 200
    (code[2],user_3, 401),# req nok missing requiered username, return status 401
    (code[2],user_4, 401) # req nok missing requiered password, return status 401 
    ])
def test_user_create(code,body,expected):
    resp = request_post("admin",code,body)
    assert (resp[0] == expected)

@pytest.mark.parametrize(
    "code,name,expected", [
    (code[0],"alice", 401), # req nok with user patrick, return status 401
    (code[2],"alice", 200), # req ok with user admin, return status 200
    (code[2],"alice", 401),# req nok username not exist, return status 401
    (code[2],"", 401) # req nok missing username, return status 401
    ])
def test_user_delete(code,name,expected):
    assert (request_delete("admin?user="+name,code) == expected)