import requests


PRODUCTION_MODE = True
URL = 'https://sharecipe-production.herokuapp.com' if PRODUCTION_MODE else 'https://sharecipe-backend.herokuapp.com'


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
dummy = Account.add('Benergy10', 'Je93ndx#', 'Code. Create. Coordinate.')
header = {'Authorization': f'Bearer {dummy.access_token}'}


# Add user profile pic
with open('seed_images/profile.jpg', 'rb') as image_file:
    test_image = {'image': image_file.read()}
response = requests.put(f'{URL}/users/{dummy.user_id}/profileimage', headers=header, files=test_image)


# Add pizza recipe
payload = {
    'name': 'Round Pizza',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
    ]
}

response = requests.put(f'{URL}/recipes', headers=header, json=payload)
pizza_recipe = response.json()

pizza_images = []
with open('seed_images/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{pizza_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Chocolate Cake',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
    ]
}

response = requests.put(f'{URL}/recipes', headers=header, json=payload)
cake_recipe = response.json()

cake_images = []
with open('seed_images/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('seed_images/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{cake_recipe["recipe_id"]}/images', headers=header, files=cake_images)


# Add nasi lemak recipe
payload = {
    'name': 'Nasi Lemak',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
    ]
}

response = requests.put(f'{URL}/recipes', headers=header, json=payload)
nasilemak_recipe = response.json()

pizza_images = []
with open('seed_images/nasilemak1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/nasilemak2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{nasilemak_recipe["recipe_id"]}/images', headers=header, files=pizza_images)


# Add cake recipe
payload = {
    'name': 'Assorted Sushi',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
    ]
}

response = requests.put(f'{URL}/recipes', headers=header, json=payload)
sushi_recipe = response.json()

cake_images = []
with open('seed_images/sushi1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('seed_images/sushi2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{sushi_recipe["recipe_id"]}/images', headers=header, files=cake_images)


# Add pizza recipe
payload = {
    'name': 'US Ribeye Steak',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5, 'unit': 'kg'}
    ]
}

response = requests.put(f'{URL}/recipes', headers=header, json=payload)
steak_recipe = response.json()

pizza_images = []
with open('seed_images/steak1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/steak2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{steak_recipe["recipe_id"]}/images', headers=header, files=pizza_images)
