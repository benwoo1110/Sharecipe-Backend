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
        # Create user accounts
        cls.user1 = Account.add('testing123', '123456', 'A human!')
        cls.user2 = Account.add('testing456', '123456')
        cls.user3 = Account.add('admin123', '123456')

    @classmethod
    def tearDownClass(cls):
        # Delete the test accounts
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()

    def test_all(self):
        user1 = self.user1
        user2 = self.user2
        user3 = self.user3

        # Hello world
        response = requests.get(f'{URL}/hello')
        data = response.json()
        self.assertDictEqual(data, {'hello': 'world'})

        # User login
        payload = {'username': 'testing123', 'password': '123456'}
        response = requests.post(f'{URL}/account/login', json=payload)
        data = response.json()
        self.assertEqual(user1.user_id, data.get('user_id'))

        # # Search users
        # header = {'Authorization': f'Bearer {user1.access_token}'}
        # response = requests.get(f'{URL}/users', headers=header)
        # data = response.json()
        # self.assertListEqual(data, [
        #     {'user_id': user1.user_id, 'username': 'testing123', 'bio': 'A human!'}, 
        #     {'user_id': user2.user_id, 'username': 'testing456', 'bio': None}, 
        #     {'user_id': user3.user_id, 'username': 'admin123', 'bio': None}
        # ])

        # # Search users with query
        # header = {'Authorization': f'Bearer {user1.access_token}'}
        # response = requests.get(f'{URL}/users?username=test', headers=header)
        # data = response.json()
        # self.assertIsInstance(data, list)
        # self.assertListEqual(data, [
        #     {'user_id': user1.user_id, 'username': 'testing123', 'bio': 'A human!'}, 
        #     {'user_id': user2.user_id, 'username': 'testing456', 'bio': None}
        # ])

        # Get user data
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.get(f'{URL}/users/{user2.user_id}', headers=header)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.matchDict(data, user_id=user2.user_id, username="testing456", bio=None)

        # Update user data
        header = {'Authorization': f'Bearer {user1.access_token}'}
        payload = {'username': 'totallyNotAdmin', 'bio': 'Code. Create. Coordinate.'}
        response = requests.patch(f'{URL}/users/{user1.user_id}', headers=header, json=payload)
        data = response.json()
        self.matchDict(data, user_id=user1.user_id, username="totallyNotAdmin", bio="Code. Create. Coordinate.")

        # Follow another user
        header = {'Authorization': f'Bearer {user1.access_token}'}
        payload = {'follow_id': user2.user_id}
        response = requests.put(f'{URL}/users/{user1.user_id}/follows', headers=header,  json=payload)

        # Follow a second user
        header = {'Authorization': f'Bearer {user1.access_token}'}
        payload = {'follow_id': user3.user_id}
        response = requests.put(f'{URL}/users/{user1.user_id}/follows', headers=header,  json=payload)

        # Get user follows
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.get(f'{URL}/users/{user1.user_id}/follows', headers=header)
        follows_data = response.json()
        self.assertEqual(len(follows_data), 2)

        # Create new recipe
        header = {'Authorization': f'Bearer {user3.access_token}'}
        payload = {
            'name': 'Edible food',
            'portion': 3,
            'difficulty': 5,
            'steps': [
                {'step_number': 1, 'name': 'a', 'description': 'Add water.'}, 
                {'step_number': 2, 'name': 'b', 'description': 'Add egg.'}
            ],
            'ingredients': [
                {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
                {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
            ]
        }
        response = requests.put(f'{URL}/recipes', headers=header, json=payload)
        recipe_data = response.json()
        self.matchDict(recipe_data, user_id=user3.user_id, name="Edible food", portion=3, difficulty=5)

        # Get all recipe
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.get(f'{URL}/users/{user3.user_id}/recipes', headers=header, json=payload)
        data = response.json()

        # Get recipe data`
        header = {'Authorization': f'Bearer {user3.access_token}'}
        response = requests.get(f'{URL}/recipes/{recipe_data["recipe_id"]}', headers=header)
        data = response.json()
        self.assertDictEqual(data, recipe_data)

        # Update recipe data
        header = {'Authorization': f'Bearer {user3.access_token}'}
        payload = {'name': 'Poison'}
        response = requests.patch(f'{URL}/recipes/{recipe_data["recipe_id"]}', headers=header, json=payload)
        data = response.json()
        self.assertEqual(data.get('name'), 'Poison')

        # Add a recipe step
        header = {'Authorization': f'Bearer {user3.access_token}'}
        payload = {'step_number': 3, 'name': 'c', 'description': 'Boil over stove.'}
        response = requests.put(f'{URL}/recipes/{recipe_data["recipe_id"]}/steps', headers=header, json=payload)
        data = response.json()
        self.matchDict(data, recipe_id=recipe_data["recipe_id"], **payload)

        # Get a recipe steps
        header = {'Authorization': f'Bearer {user3.access_token}'}
        response = requests.get(f'{URL}/recipes/{recipe_data["recipe_id"]}/steps', headers=header, json=payload)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)

        # Add recipe images
        header = {'Authorization': f'Bearer {user3.access_token}'}
        test_images = []
        with open('tests/test1.png', 'rb') as image_file:
            test_images.append(('images', image_file.read()))
        with open('tests/test2.png', 'rb') as image_file:
            test_images.append(('images', image_file.read()))
        with open('tests/test3.png', 'rb') as image_file:
            test_images.append(('images', image_file.read()))
        response = requests.put(f'{URL}/recipes/{recipe_data["recipe_id"]}/images', headers=header, files=test_images)

        # Get recipe images
        header = {'Authorization': f'Bearer {user3.access_token}'}
        response = requests.get(f'{URL}/recipes/{recipe_data["recipe_id"]}/images', headers=header)
        self.assertEqual(response.status_code, 200)
        with open('tests/recipe_images.zip', "wb") as file:
            file.write(response.content)

        # User like recipe
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.put(f'{URL}/recipes/{recipe_data["recipe_id"]}/likes', headers=header)
        self.assertEqual(response.status_code, 201)

        # Another user like recipe
        header = {'Authorization': f'Bearer {user2.access_token}'}
        response = requests.put(f'{URL}/recipes/{recipe_data["recipe_id"]}/likes', headers=header)
        self.assertEqual(response.status_code, 201)

        # Get user likes
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.get(f'{URL}/users/{user1.user_id}/recipes/likes', headers=header)
        like_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(like_data), 1)
        
        # Get recipe likes
        response = requests.get(f'{URL}/recipes/{recipe_data["recipe_id"]}/likes', headers=header)
        like_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(like_data), 2)

        # User unlike recipe
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.delete(f'{URL}/recipes/{recipe_data["recipe_id"]}/likes', headers=header)
        self.assertEqual(response.status_code, 204)

        # User doesnt have likes
        header = {'Authorization': f'Bearer {user1.access_token}'}
        response = requests.get(f'{URL}/users/{user1.user_id}/recipes/likes', headers=header)
        like_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(like_data), 0)

        # Delete recipe
        header = {'Authorization': f'Bearer {user3.access_token}'}
        response = requests.delete(f'{URL}/recipes/{recipe_data["recipe_id"]}', headers=header)
        self.assertEqual(response.status_code, 204)
        response = requests.get(f'{URL}/recipes/{recipe_data["recipe_id"]}', headers=header)
        self.assertEqual(response.status_code, 404)

        # Upload profile image
        header = {'Authorization': f'Bearer {user2.access_token}'}
        with open('tests/test.png', 'rb') as image_file:
            test_image = {'image': image_file.read()}
        response = requests.put(f'{URL}/users/{user2.user_id}/profileimage', headers=header, files=test_image)
        self.assertEqual(response.status_code, 200)

        # Download profile image
        header = {'Authorization': f'Bearer {user2.access_token}'}
        response = requests.get(f'{URL}/users/{user2.user_id}/profileimage', headers=header)
        self.assertEqual(response.status_code, 200)
        with open('tests/downloaded_test.png', "wb") as file:
            file.write(response.content)

        # Delete profile image
        header = {'Authorization': f'Bearer {user2.access_token}'}
        response = requests.delete(f'{URL}/users/{user2.user_id}/profileimage', headers=header)
        self.assertEqual(response.status_code, 200)

    def matchDict(self, actual, **expected):
        for key, value in expected.items():
            self.assertEqual(actual.get(key), value)


if __name__ == '__main__':
    unittest.main()
