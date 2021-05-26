import unittest
import requests


use_production = False
URL = 'https://sharecipe-backend.herokuapp.com' if use_production else 'http://127.0.0.1:5000'


class Account:
    def __init__(self, user_id, access_token, refresh_token):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def delete(self):
        header = {'Authorization': f'Bearer {self.refresh_token}'}
        response = requests.delete(f'{URL}/account/delete', headers=header)

    @classmethod
    def add(cls, username, password):
        payload = {'username': username, 'password': password}
        response = requests.post(f'{URL}/account/register', json=payload)
        return cls(**response.json())


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a1 = Account.add('testing123', '123456')
        cls.a2 = Account.add('testing456', '123456')
        cls.a3 = Account.add('admin123', '123456')

    def test_hello_world(self):
        response = requests.get(f'{URL}/hello')
        data = response.json()
        self.assertDictEqual(data, {'hello': 'world'})

    def test_user_login(self):
        payload = {'username': 'testing123', 'password': '123456'}
        response = requests.post(f'{URL}/account/login', json=payload)
        data = response.json()
        self.assertEqual(self.a1.user_id, data.get('user_id'))

    def test_user_search(self):
        header = {'Authorization': f'Bearer {self.a1.access_token}'}
        response = requests.get(f'{URL}/users', headers=header)
        data = response.json()
        self.assertListEqual(data, [
            {'user_id': self.a1.user_id, 'username': 'testing123', 'bio': None}, 
            {'user_id': self.a2.user_id, 'username': 'testing456', 'bio': None}, 
            {'user_id': self.a3.user_id, 'username': 'admin123', 'bio': None}
        ])

    def test_user_search_with_query(self):
        header = {'Authorization': f'Bearer {self.a1.access_token}'}
        response = requests.get(f'{URL}/users?username=test', headers=header)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertListEqual(data, [
            {'user_id': self.a1.user_id, 'username': 'testing123', 'bio': None}, 
            {'user_id': self.a2.user_id, 'username': 'testing456', 'bio': None}
        ])

    def test_user_get_data(self):
        header = {'Authorization': f'Bearer {self.a1.access_token}'}
        response = requests.get(f'{URL}/users/{self.a2.user_id}', headers=header)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertDictEqual(data, {'user_id': self.a2.user_id, 'username': 'testing456', 'bio': None})

    def test_user_update_data(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        payload = {'username': 'totallyNotAdmin', 'bio': 'Code. Create. Coordinate.'}
        response = requests.patch(f'{URL}/users/{self.a3.user_id}', headers=header, json=payload)
        data = response.json()
        self.assertDictEqual(data, {'user_id': self.a3.user_id, 'username': 'totallyNotAdmin', 'bio': 'Code. Create. Coordinate.'})

    @classmethod
    def tearDownClass(cls):
        cls.a1.delete()
        cls.a2.delete()
        cls.a3.delete()


if __name__ == '__main__':
    unittest.main()
