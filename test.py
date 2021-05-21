import unittest
import requests


use_production = False
URL = 'https://sharecipe-backend.herokuapp.com' if use_production else 'http://127.0.0.1:5000'


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = {'username': 'testing123', 'password': '123456'}
        response = requests.post(f'{URL}/register', json=payload)
        data = response.json()
        cls.user_id = data['user_id']
        cls.token = data['token']

    def test_hello_world(self):
        response = requests.get(f'{URL}/hello')
        data = response.json()
        self.assertDictEqual(data, {'hello': 'world'})

    def tearDownClass(cls):
        response = requests.delete(f'{URL}/user/{TestAPI.user_id}')


if __name__ == '__main__':
    unittest.main()
