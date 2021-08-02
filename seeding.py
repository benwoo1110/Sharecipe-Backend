import requests


PRODUCTION_MODE = True
URL = 'https://sharecipe-production.herokuapp.com' if PRODUCTION_MODE else 'http://127.0.0.1:5000'


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


# Create jia hao
jh = Account.add('jiahao', '12345678', 'Available.')
jh_header = {'Authorization': f'Bearer {jh.access_token}'}

# Create melvin
mv = Account.add('melvin', '12345678', 'Cooking madness!!!')
mv_header = {'Authorization': f'Bearer {mv.access_token}'}

# Add melvin recipe
payload = {
    'name': 'Steak and Potatoes',
    'description': 'Fluffy and crispy potatoes roasted beautifully in the oven with goose fat and served with tender, medium rare New York Strips infused with garlic, butter and herbs.',
    'total_time_needed': 3600,
    'portion': 2,
    'difficulty': 3,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Wash and prepare the potatoes and place them into a large pot of water with a generous amount of salt and some baking soda'}, 
        {'step_number': 2, 'description': 'Parboil the potatoes for about 10 minutes'}, 
        {'step_number': 3, 'description': 'Drain the potatoes and shake them in the pot a little. The steam helps the potatoes to dry out'},
        {'step_number': 4, 'description': 'Lay potatoes on a baking sheet and drizzle with olive oil, goose fat, 2 cloves of garlic and some rosemary. Roast in a 200 degree oven for about 45 minutes to 1 hour'},
        {'step_number': 5, 'description': 'Season the steaks on both sides generously with salt and pepper'},
        {'step_number': 6, 'description': 'Sear in a ripping hot cast iron skillet using an oil with a high smoke point, like canola or peanut oil'},
        {'step_number': 7, 'description': 'Cook steaks to desired doneness, then lower the heat and add the butter, crushed garlic, rosemary and thyme'},
        {'step_number': 8, 'description': 'Baste the steaks for about 30 seconds'},
        {'step_number': 9, 'description': 'Serve, finishing with a touch of freshly-ground black pepper'}
    ],
    'ingredients': [
        {'name': 'Steak', 'quantity': 2.0, 'unit': ''},
        {'name': 'Yukon gold potatoes', 'quantity': 6.0, 'unit': ''},
        {'name': 'Baking soda', 'quantity': 2.0, 'unit': 'tsp'},
        {'name': 'Olive oil', 'quantity': 2.0, 'unit': 'tbsp'},
        {'name': 'Goose fat', 'quantity': 3.0, 'unit': 'tbsp'},
        {'name': 'Garlic', 'quantity': 4.0, 'unit': 'cloves'},
        {'name': 'Thyme', 'quantity': 1.0, 'unit': 'bunch'},
        {'name': 'Rosemary', 'quantity': 1.0, 'unit': 'bunch'},
        {'name': 'Butter', 'quantity': 2.0, 'unit': 'tbsp'}
    ],
    'tags': [
        {'name': 'american'},
        {'name': 'western'},
        {'name': 'meat'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=mv_header, json=payload)
steak_potato_recipe = response.json()
steak_potato_images = []
with open('seed_images/steak_1.jpg', 'rb') as image_file:
    steak_potato_images.append(('images', image_file.read()))
with open('seed_images/steak_2.jpg', 'rb') as image_file:
    steak_potato_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{steak_potato_recipe["recipe_id"]}/images', headers=mv_header, files=steak_potato_images)

# Add jia hao recipes
# Add pizza recipe
payload = {
    'name': 'Round Pizza',
    'description': 'A pizza',
    'total_time_needed': 3600,
    'portion': 3,
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10.0, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 10.0, 'unit': 'kg'}
    ],
    'tags': [
        {'name': 'italian'},
        {'name': 'western'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=jh_header, json=payload)
pizza_recipe = response.json()
pizza_images = []
with open('seed_images/pizza1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/pizza2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{pizza_recipe["recipe_id"]}/images', headers=jh_header, files=pizza_images)

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
        {'name': 'Egg', 'quantity': 10.9, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5.0, 'unit': 'kg'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=jh_header, json=payload)
cake_recipe = response.json()
cake_images = []
with open('seed_images/cake1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('seed_images/cake2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{cake_recipe["recipe_id"]}/images', headers=jh_header, files=cake_images)

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
        {'name': 'Egg', 'quantity': 10.0, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5.8, 'unit': 'kg'}
    ],
    'tags': [
        {'name': 'malay'},
        {'name': 'rice'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=jh_header, json=payload)
nasilemak_recipe = response.json()
pizza_images = []
with open('seed_images/nasilemak1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/nasilemak2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{nasilemak_recipe["recipe_id"]}/images', headers=jh_header, files=pizza_images)

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
        {'name': 'Egg', 'quantity': 10.8, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5.9, 'unit': 'kg'}
    ],
    'tags': [
        {'name': 'sweet'},
        {'name': 'cake'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=jh_header, json=payload)
sushi_recipe = response.json()
cake_images = []
with open('seed_images/sushi1.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
with open('seed_images/sushi2.jpg', 'rb') as image_file:
    cake_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{sushi_recipe["recipe_id"]}/images', headers=jh_header, files=cake_images)

# Add steak recipe
payload = {
    'name': 'US Ribeye Steak',
    'difficulty': 5,
    'is_public': True,
    'steps': [
        {'step_number': 1, 'description': 'Add water.'}, 
        {'step_number': 2, 'description': 'Add egg.'}
    ],
    'ingredients': [
        {'name': 'Egg', 'quantity': 10.7, 'unit': 'grams'},
        {'name': 'Water', 'quantity': 5.9, 'unit': 'kg'}
    ]
}
response = requests.put(f'{URL}/recipes', headers=jh_header, json=payload)
steak_recipe = response.json()
pizza_images = []
with open('seed_images/steak1.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
with open('seed_images/steak2.jpg', 'rb') as image_file:
    pizza_images.append(('images', image_file.read()))
response = requests.put(f'{URL}/recipes/{steak_recipe["recipe_id"]}/images', headers=jh_header, files=pizza_images)
