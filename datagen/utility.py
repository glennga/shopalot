#!/usr/local/bin/python3
import random
import string
import decimal


STORE_NAMES = [
    "Machias Mainway",
    "Casey's Cove Convenience Store",
    "Maay Convenient Inc",
    "Cefco",
    "Mapco Express",
    "Plaid Pantry",
    "Jackson Food Store",
    "Rutters Farm Store",
    "Irving Oil Corp",
    "Hillcrest",
    "Cubbys",
    "7-Eleven",
    "Service Champ",
    "Express Mart Stores",
    "Baum's Mercantile",
    "Border Station",
    "Country Market",
    "Golden Spike Travel Plaza",
    "Wesco Oil CO",
    "Cracker Barrel Stores Inc",
    "Elnemr Enterprises Inc",
    "Sheetz",
    "Pump-N-Pantry Of NY",
    "Spaceway Oil CO",
    "6-Twelve Convenient-Mart Inc",
    "Dandy Mini Mart",
    "Stripes Llc",
    "Plaid Pantries Inc",
    "Quick Chek Food Stores",
    "Victory Marketing Llc",
    "Beasley Enterprises Inc",
    "Lil' Champ",
    "Pit Row",
    "Popeye Shell Superstop",
    "Mapco",
    "Sunset Foods",
    "Simonson Market",
    "Fasmart",
    "Super Quik Inc",
    "Jim's Quick Stop"
]

PRODUCT_CATEGORIES = [
    'Baby Care', 'Beverages', 'Bread & Bakery', 'Breakfast & Cereal', 'Canned Goods & Soups',
    'Condiments, Spice, & Bake', 'Cookies, Snacks, & Candy', 'Dairy, Eggs, & Cheese', 'Deli', 'Frozen Foods',
    'Fruits & Vegetables', 'Grains, Pasta, & Sides', 'Meat & Seafood', 'Paper, Cleaning, & Home',
    'Personal Care & Health', 'Pet Care'
]

PHONE_TYPES = ['HOME', 'OFFICE', 'MOBILE']

UNIQUE_ID_MAP = {}


def products_filename_to_product_category(filename):
    return {
        "baby-care.json": "Baby Care",
        "beverages.json": "Beverages",
        "bread-bakery.json": "Bread & Bakery",
        "breakfast-cereal.json": "Breakfast & Cereal",
        "canned-goods-soups.json": "Canned Goods & Soups",
        "condiments-spice-bake.json": "Condiments, Spice, & Bake",
        "cookies-snacks-candy.json": "Cookies, Snacks, & Candy",
        "dairy-eggs-cheese.json": "Dairy, Eggs, & Cheese",
        "deli.json": "Deli",
        "frozen-foods.json": "Frozen Foods",
        "fruits-vegetables.json": "Fruits & Vegetables",
        "grains-pasta-sides.json": "Grains, Pasta, & Sides",
        "meat-seafood.json": "Meat & Seafood",
        "paper-cleaning-home.json": "Paper, Cleaning, & Home",
        "personal-care-health.json": "Personal Care & Health",
        "pet-care.json": "Pet Care"
    }[filename]


def user_name_to_user_email(first_name, last_name):
    choices = [1, 2, 3, 4]
    choice = random.choice(choices)

    # We have a 20% chance that our first name is capitalized.
    is_first_name_capitalized = random.choices([True, False], weights=[0.2, 0.8], k=1)[0]

    # We have a 20% chance that our first name is abbreviated.
    is_first_name_abb = random.choices([True, False], weights=[0.2, 0.8], k=1)[0]

    # We have a 20% chance that our last name is capitalized.
    is_last_name_capitalized = random.choices([True, False], weights=[0.2, 0.8], k=1)[0]

    # We have a 10% chance that numbers are in the front of this user's email.
    are_numbers_in_front = random.choices([True, False], weights=[0.1, 0.9], k=1)[0]

    # We have a 70% chance our users have emails from gmail.
    email_suffix = random.choices(['@gmail.com', '@yahoo.com', '@hotmail.com', '@aol.com'],
                                  weights=[0.7, 0.1, 0.1, 0.1], k=1)[0]

    working_email = ''
    if is_first_name_abb:
        first_name = first_name[:3]
    if are_numbers_in_front:
        number_of_numbers = random.choice([2, 3, 4, 5])
        for _ in range(number_of_numbers):
            working_email = working_email + str(random.randint(0, 9))

    # Choice #1: first name + random numbers
    if choice == 1:
        number_of_numbers = random.choice([2, 3, 4, 5])
        if is_first_name_capitalized:
            working_email = working_email + first_name.capitalize()
        else:
            working_email = working_email + first_name.lower()

        for _ in range(number_of_numbers):
            working_email = working_email + str(random.randint(0, 9))

    # Choice #2: last name + random numbers
    elif choice == 2:
        number_of_numbers = random.choice([2, 3, 4, 5])
        if is_last_name_capitalized:
            working_email = working_email + last_name.capitalize()
        else:
            working_email = working_email + last_name.lower()
        for _ in range(number_of_numbers):
            working_email = working_email + str(random.randint(0, 9))

    # Choice #3: first name + last name with _, ., or nothing in between, maybe numbers at the end
    # Choice #4: last name + first name with _, ., or nothing in between, maybe numbers at the end
    elif choice == 3 or choice == 4:
        intermediate_char = random.choice(['_', '.', ''])
        are_numbers_at_end = random.choice([True, False])

        if choice == 3:
            if is_first_name_capitalized:
                working_email = working_email + first_name.capitalize()
            else:
                working_email = working_email + first_name.lower()

            working_email = working_email + intermediate_char
            if is_last_name_capitalized:
                working_email = working_email + last_name.capitalize()
            else:
                working_email = working_email + last_name.lower()
        else:
            if is_last_name_capitalized:
                working_email = working_email + last_name.capitalize()
            else:
                working_email = working_email + last_name.lower()

            working_email = working_email + intermediate_char

            if is_first_name_capitalized:
                working_email = working_email + first_name.capitalize()
            else:
                working_email = working_email + first_name.lower()

        if are_numbers_at_end:
            number_of_numbers = random.choice([2, 3, 4, 5])
            for _ in range(number_of_numbers):
                working_email = working_email + str(random.randint(0, 9))

    return working_email + email_suffix


def product_to_order_item(product):
    if type(product[1]) is not str:
        price = max(product[1] + (product[1] * random.random()) - (product[1] / 2.0), 0.99)
        price = decimal.Decimal(price).quantize(decimal.Decimal('0.01'), decimal.ROUND_HALF_UP)
        price = float(price)
    else:
        price = None
    return {
        'product_id': product[0],
        'price': price
    }


def repeat_and_collect(func, success_prob=None, minimum_times=None, is_distinct=False):
    results = []
    if minimum_times is not None:
        for _ in range(minimum_times):
            result = func()
            while is_distinct and result in results:
                result = func()
            results.append(func())
    if success_prob is not None:
        while success_prob():
            result = func()
            while is_distinct and result in results:
                result = func()
            results.append(func())
    return results


def insert_missing_or_null(record, null_dist, missing_dist):
    for k, v in null_dist.items():
        if v():
            key_steps = k.split('.')
            working_dict = record
            while len(key_steps) > 1:
                working_dict = working_dict[key_steps.pop(0)]
            working_dict[key_steps.pop(0)] = None

    for k, v in missing_dist.items():
        if v():
            key_steps = k.split('.')
            working_dict = record
            while len(key_steps) > 1:
                working_dict = working_dict[key_steps.pop(0)]
            del working_dict[key_steps.pop(0)]


def get_unique_id(domain_key, id_length=5):
    def generate_ids():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(id_length))

    global UNIQUE_ID_MAP
    if domain_key not in UNIQUE_ID_MAP:
        UNIQUE_ID_MAP[domain_key] = set()

    # Ensure that we only generate unique IDs, in the context of the given domain.
    candidate_id = generate_ids()
    while candidate_id in UNIQUE_ID_MAP[domain_key]:
        candidate_id = generate_ids()
    UNIQUE_ID_MAP[domain_key].add(candidate_id)

    # Return this unique ID back to the user.
    return candidate_id


def generate_hours():
    hours_list = []
    for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        if random.choices([True, False], weights=[0.8, 0.2], k=1)[0]:
            hours_list.append({'day': day,
                               'opens': random.choice(['8AM', '10AM', '12PM']),
                               'closes': random.choice(['4PM', '8PM', '10PM'])})
    return hours_list
