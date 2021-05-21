import unittest
import requests


use_production = False
URL = 'https://sharecipe-backend.herokuapp.com' if use_production else 'http://127.0.0.1:5000'


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = {'username': 'testing123', 'password': '123456'}
        response = requests.post(f'{URL}/account/register', json=payload)
        data = response.json()
        print(data)
        cls.user_id = data['user_id']
        cls.access_token = data['access_token']
        cls.refresh_token = data['refresh_token']

    def test_hello_world(self):
        response = requests.get(f'{URL}/hello')
        data = response.json()
        self.assertDictEqual(data, {'hello': 'world'})

    def test_user_login(self):
        payload = {'username': 'testing123', 'password': '123456'}
        response = requests.post(f'{URL}/account/login', json=payload)
        data = response.json()
        print(data)

    @classmethod
    def tearDownClass(cls):
        header = {'Authorization': f'Bearer {cls.access_token}'}
        response = requests.delete(f'{URL}/account/delete', headers=header)


if __name__ == '__main__':
    unittest.main()
