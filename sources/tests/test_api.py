import requests
import unittest
# ast library is used to convert string from response.text to a dictionary in order to extract the token of the user created in the token section
import ast

class TestEncryption(unittest.TestCase):
    def setUp(self):
    # data to test
        self.test_user = "Regissssssfffsssdddddxsdddssssss"
        self.test_password = "Roberte"
        #self.user_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ"
################################################################NEW_USER########################################################
    def test_response_new_user(self):
    # Try to create a new user (That will only test the response status_code)
        self.headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ',
    'Content-Type': 'application/json',}
        self.json_data = {"username": self.test_user,"password_hash": self.test_password}
        self.response = requests.post('http://127.0.0.1:8000/users', headers=self.headers, json=self.json_data)
        self.assertEqual(self.response.status_code,200, "the response is supposed to be 200 but {} instead".format(self.response.status_code))
    def test_response_new_old_user(self):
    # Try to create an admin new user (That will only test the response status_code)
        self.headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ',
    'Content-Type': 'application/json',}
        self.json_data = {"username": "admin","password_hash": "LambdaPassword"}
        self.response = requests.post('http://127.0.0.1:8000/users', headers=self.headers, json=self.json_data)
        self.assertEqual(self.response.status_code,422, "the response is supposed to be 422 but {} instead".format(self.response.status_code))
################################################################TOKEN########################################################
    def test_token_generator(self):
    # Test the token generation for the newly created user (That will only test the response status_code)
        self.headers = {
    'accept': 'application/json',}
        self.data = {
    'grant_type': '',
    'username': self.test_user,
    'password': self.test_password,
    'scope': '',
    'client_id': '',
    'client_secret': '',}
        self.response = requests.post('http://127.0.0.1:8000/token', headers=self.headers, data=self.data)
        # In this part we'll asign the token to a varible to test the permission of this user bellow 
        self.user_token = ast.literal_eval(self.response.text)['access_token']
        self.assertEqual(self.response.status_code,200, "the response is supposed to be 200 but {} instead".format(self.response.status_code))
        return self.user_token
################################################################GET_USER######################################################
    def test_get_user_not_authenticated(self):
        # Try to get user while not authenticated
        self.headers = {
    'accept': 'application/json',}
        self.response = requests.get('http://127.0.0.1:8000/users/me', headers=self.headers)
        self.assertEqual(self.response.status_code,401, "the response is supposed to be 401 but {} instead".format(self.response.status_code))
    def test_get_user_authenticated(self):
        # Try to get user while authenticated to the new user created above
        self.user_token = self.test_token_generator() # Inherite the token from test_token_generator()
        self.headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer {}'.format(self.user_token),}
        self.response = requests.get('http://127.0.0.1:8000/users/me', headers=self.headers)
        self.assertEqual(self.response.status_code,200, "the response is supposed to be 200 but {} instead".format(self.response.status_code))
################################################################MODELS########################################################
    def test_model_v0_not_authenticated(self):
    # Test the model prediction status_code while not authenticated
        self.headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',}
        self.json_data = {
    'distance_from_home': 0,
    'distance_from_last_transaction': 0,
    'ratio_to_median_purchase_price': 0,
    'repeat_retailer': 0,
    'used_chip': 0,
    'used_pin_number': 0,
    'online_order': 0,}
        self.response = requests.post('http://127.0.0.1:8000/users/predict/v0', headers=self.headers, json=self.json_data)
        self.assertEqual(self.response.status_code,401, "the response is supposed to be 401 but {} instead".format(self.response.status_code))
    def test_model_v0_authenticated(self):
    # Test the model prediction status_code while authenticated as the admin
        self.headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInBhc3N3b3JkX2hhc2giOiIkMmIkMTIkLkp0QW5lQk9EV2ZGMjlzZEpiQ2djZUs4VUtqSVNSU2tpM3ZIUklQN09NeWsueHNUTzQ5TkcifQ.wWQTmRV0NsXzma64KmRIEaToqga6bk_UJGD7NR3r9dQ',
    'Content-Type': 'application/json',}
        self.json_data = {
    'distance_from_home': 0,
    'distance_from_last_transaction': 0,
    'ratio_to_median_purchase_price': 0,
    'repeat_retailer': 0,
    'used_chip': 0,
    'used_pin_number': 0,
    'online_order': 0,}
        self.response = requests.post('http://127.0.0.1:8000/users/predict/v0', headers=self.headers, json=self.json_data)
        self.assertEqual(self.response.status_code,200, "the response is supposed to be 200 but {} instead".format(self.response.status_code))
    def test_model_v1_authenticated(self):
        # Test the model prediction vi status_code while authenticated as the newly created user
        self.user_token = self.test_token_generator() # Inherite the token from test_token_generator()
        self.headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer {}'.format(self.user_token),
    'Content-Type': 'application/json',}
        self.json_data = {
    'distance_from_home': 0,
    'distance_from_last_transaction': 0,
    'ratio_to_median_purchase_price': 0,
    'repeat_retailer': 0,
    'used_chip': 0,
    'used_pin_number': 0,
    'online_order': 0,}
        self.response = requests.post('http://127.0.0.1:8000/users/predict/v1', headers=self.headers, json=self.json_data)
        self.assertEqual(self.response.status_code,200, "the response is supposed to be 200 but {} instead".format(self.response.status_code))
if __name__ == "__main__":
    unittest.main()