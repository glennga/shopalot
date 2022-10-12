import argparse
import json
import random
import faker
import csv

from datagen import utility

# Define the fields that will appear in a Stores document.
REQUIRED_FIELDS = ['store_id', 'address', 'name', 'phone', 'hours']
NULLABLE_FIELDS = []
MISSABLE_FIELDS = ['address.zip_code', 'categories']
ALL_FIELDS = [f for f in set(REQUIRED_FIELDS + NULLABLE_FIELDS + MISSABLE_FIELDS) if '.' not in f]

# Define the **valued** distribution for each field. These must match the fields above.
VALUED_DISTRIBUTIONS = {
    # Each value in this dictionary is a function with the Faker data generator as the first argument (f) and a
    # random zip code row as the second argument (z).

    # A unique 5-digit alphanumeric store ID for each store.
    'store_id': lambda f, z: utility.get_unique_id('store', id_length=5),

    # An address is composed of a street, city, zip_code, and state.
    'address': lambda f, z: {
        'street': f.street_address(),
        'city': z['primary_city'],
        'state': z['state'],
        'zip_code': z['zip']
    },

    # A store name is randomly drawn from a pool we created earlier.
    'name': lambda f, z: random.choice(utility.STORE_NAMES),

    # A phone is randomly generated with Faker.
    'phone': lambda f, z: f.phone_number(),

    # A categories array is composed of categories from our products, with a minimum size of 3.
    'categories': lambda f, z: utility.repeat_and_collect(
        func=lambda: random.choice(utility.PRODUCT_CATEGORIES),
        minimum_times=random.randint(3, len(utility.PRODUCT_CATEGORIES)),
        is_distinct=True
    ),

    'hours': lambda f, u: utility.generate_hours()
}

# Define the missing and null distributions for each field. These must match the fields above. You can use the "."
# notation to specify nested fields.
NULL_DISTRIBUTIONS = {
}
MISSING_DISTRIBUTIONS = {
    # A zip code has a 1% chance of being omitted.
    'address.zip_code': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0],

    # A categories array has a 1% chance of being omitted.
    'categories': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0],
}


def generate_stores(stores_count, zip_code_file, fake_data_generator, output_file):
    zip_codes = []
    with open(zip_code_file, newline='') as f:
        zip_code_reader = csv.DictReader(f)
        for row in zip_code_reader:
            zip_codes.append(row)

    with open(output_file, 'w') as output_fp:
        for _ in range(stores_count):
            stores_dict = {}
            for field in ALL_FIELDS:
                stores_dict[field] = VALUED_DISTRIBUTIONS[field](fake_data_generator, random.choice(zip_codes))
            utility.insert_missing_or_null(stores_dict, NULL_DISTRIBUTIONS, MISSING_DISTRIBUTIONS)
            json.dump(stores_dict, output_fp)
            output_fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the Stores dataset.')
    parser.add_argument('--store_count', type=int, default=400, help='Number of stores to generate.')
    parser.add_argument('--output_file', default='stores.json', help='Location of the output Stores dataset.')
    parser.add_argument('--random_seed', default=0, help='Seed used for Faker and the random package.')
    parser.add_argument('--zip_code_file', default='external/zip-code-data.csv', help='Location of the zip-code CSV.')
    arguments = parser.parse_args()

    # Seed our RNG.
    faker.Faker.seed(arguments.random_seed)
    random.seed(arguments.random_seed)

    # Generate our stores.
    generate_stores(arguments.store_count, arguments.zip_code_file, faker.Faker(), arguments.output_file)
