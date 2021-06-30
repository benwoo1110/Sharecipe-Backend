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
    def add(cls, username, password, bio=None):
        payload = {'username': username, 'password': password, 'bio': bio}
        response = requests.post(f'{URL}/account/register', json=payload)
        return cls(**response.json())


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a1 = Account.add('testing123', '123456', 'A human!')
        cls.a2 = Account.add('testing456', '123456')
        cls.a3 = Account.add('admin123', '123456')
        cls.maxDiff = None

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
            {'user_id': self.a1.user_id, 'username': 'testing123', 'bio': 'A human!'}, 
            {'user_id': self.a2.user_id, 'username': 'testing456', 'bio': None}, 
            {'user_id': self.a3.user_id, 'username': 'admin123', 'bio': None}
        ])

    def test_user_search_with_query(self):
        header = {'Authorization': f'Bearer {self.a1.access_token}'}
        response = requests.get(f'{URL}/users?username=test', headers=header)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertListEqual(data, [
            {'user_id': self.a1.user_id, 'username': 'testing123', 'bio': 'A human!'}, 
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

    def test_create_new_recipe(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        payload = {'name': 'Edible food', 'steps': [{'step_number': 1, 'name': 'a', 'description': 'Add water.'}, {'step_number': 2, 'name': 'b', 'description': 'Add egg.'}]}
        response = requests.put(f'{URL}/users/{self.a3.user_id}/recipes', headers=header, json=payload)
        data = response.json()
        TestAPI.test_recipe = data

    def test_data_get_recipe(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        response = requests.get(f'{URL}/users/{self.a3.user_id}/recipes/{TestAPI.test_recipe.get("recipe_id")}', headers=header)
        data = response.json()
        self.assertDictEqual(data, TestAPI.test_recipe)

    def test_patch_recipe(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        payload = {'name': 'Poison'}
        response = requests.patch(f'{URL}/users/{self.a3.user_id}/recipes/{TestAPI.test_recipe.get("recipe_id")}', headers=header, json=payload)
        data = response.json()
        self.assertEqual(data.get('name'), 'Poison')

    def test_recipe_delete(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        response = requests.delete(f'{URL}/users/{self.a3.user_id}/recipes/{TestAPI.test_recipe.get("recipe_id")}', headers=header)
        self.assertEqual(response.status_code, 204)
        response = requests.get(f'{URL}/users/{self.a3.user_id}/recipes/{TestAPI.test_recipe.get("recipe_id")}', headers=header)
        self.assertEqual(response.status_code, 404)

    def test_profile_image0_upload(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        with open('test.png', 'rb') as image_file:
            test_image = {'image': image_file}
            response = requests.put(f'{URL}/users/{self.a3.user_id}/profileimage', headers=header, files=test_image)
            self.assertEqual(response.status_code, 200)

    def test_profile_image1_download(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        response = requests.get(f'{URL}/users/{self.a3.user_id}/profileimage', headers=header)
        self.assertEqual(response.status_code, 200)
        with open('downloaded_test.png', "wb") as file:
            file.write(response.content)
        #TODO Check file equality

    def test_profile_image2_delete(self):
        header = {'Authorization': f'Bearer {self.a3.access_token}'}
        response = requests.delete(f'{URL}/users/{self.a3.user_id}/profileimage', headers=header)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        cls.a1.delete()
        cls.a2.delete()
        cls.a3.delete()


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
