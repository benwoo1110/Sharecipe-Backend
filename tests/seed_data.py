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


# Create user
dummy = Account.add('dummy', '1234', 'Code. Create. Coordinate')
header = {'Authorization': f'Bearer {dummy.access_token}'}


# Add user profile pic
with open('tests/profile.jpg', 'rb') as image_file:
    test_image = {'image': image_file.read()}
response = requests.put(f'{URL}/users/{dummy.user_id}/profileimage', headers=header, files=test_image)


# Add pizza recipe
payload = {
    'name': 'Round Pizza',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
pizza_recipe = response.json()

pizza_images = []
with open('tests/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('tests/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{pizza_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Chocolate Cake',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
cake_recipe = response.json()

cake_images = []
with open('tests/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('tests/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{cake_recipe["recipe_id"]}/images', headers=header, files=cake_images)


# Add pizza recipe
payload = {
    'name': 'Round Pizza',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
pizza_recipe = response.json()

pizza_images = []
with open('tests/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('tests/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{pizza_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Chocolate Cake',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
cake_recipe = response.json()

cake_images = []
with open('tests/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('tests/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{cake_recipe["recipe_id"]}/images', headers=header, files=cake_images)


# Add pizza recipe
payload = {
    'name': 'Round Pizza',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
pizza_recipe = response.json()

pizza_images = []
with open('tests/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('tests/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{pizza_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Chocolate Cake',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
cake_recipe = response.json()

cake_images = []
with open('tests/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('tests/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{cake_recipe["recipe_id"]}/images', headers=header, files=cake_images)


# Add pizza recipe
payload = {
    'name': 'Round Pizza',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
pizza_recipe = response.json()

pizza_images = []
with open('tests/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('tests/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{pizza_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Chocolate Cake',
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

response = requests.put(f'{URL}/users/{dummy.user_id}/recipes', headers=header, json=payload)
cake_recipe = response.json()

cake_images = []
with open('tests/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('tests/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/users/{dummy.user_id}/recipes/{cake_recipe["recipe_id"]}/images', headers=header, files=cake_images)
