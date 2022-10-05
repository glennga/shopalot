import argparse
import json
import os
import random
import faker

from datagen import utility

# Define the fields that will appear in a Products document.
REQUIRED_FIELDS = ['product_id', 'category', 'name', 'list_price']
NULLABLE_FIELDS = ['description']
MISSABLE_FIELDS = []
ALL_FIELDS = [f for f in set(REQUIRED_FIELDS + NULLABLE_FIELDS + MISSABLE_FIELDS) if '.' not in f]

# Define the **valued** distribution for each field. These must match the fields above.
VALUED_DISTRIBUTIONS = {
    # Each value in this dictionary is a function with the product from the scraped file as the first argument (p),
    # and the filename (f) as the second argument.

    # A unique 5-digit alphanumeric product ID for each product.
    'product_id': lambda p, f: utility.get_unique_id('product', id_length=5),

    # Use the filename to determine our product category.
    'category': lambda p, f: utility.products_filename_to_product_category(f),

    # Use the product name as is, and the shelf name as the description.
    'name': lambda p, f: p['name'],
    'description': lambda p, f: p['shelfName'],

    # Our list price has a floor of 0.99, with a 1% chance of being one of the text values.
    'list_price': lambda p, f: random.choices(
        [max(p['basePrice'], 0.99), random.choice(['tbd', 'expensive', 'pricey', 'TBD', 'TODO'])],
        weights=[0.99, 0.01])[0]
}

# Define the missing and null distributions for each field. These must match the fields above. You can use the "."
# notation to specify nested fields.
NULL_DISTRIBUTIONS = {
    # Our description has a 1% chance of being NULL.
    'description': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
}
MISSING_DISTRIBUTIONS = {
}


def generate_products(product_files, output_file):
    with open(output_file, 'w') as output_fp:
        for product_file in os.listdir(product_files):
            with open(product_files + product_file) as working_fp:
                working_json = json.load(working_fp)

            for product in working_json['response']['docs']:
                product_dict = {}
                for field in ALL_FIELDS:
                    product_dict[field] = VALUED_DISTRIBUTIONS[field](product, product_file)
                utility.insert_missing_or_null(product_dict, NULL_DISTRIBUTIONS, MISSING_DISTRIBUTIONS)
                json.dump(product_dict, output_fp)
                output_fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the Products dataset.')
    parser.add_argument('--output_file', default='products.json', help='Location of the output Products dataset.')
    parser.add_argument('--random_seed', default=0, help='Seed used for Faker and the random package.')
    parser.add_argument('--product_files', default='external/products/', help='Location of the scraped product files.')
    arguments = parser.parse_args()

    # Seed our RNG.
    faker.Faker.seed(arguments.random_seed)
    random.seed(arguments.random_seed)

    # Generate our products.
    generate_products(arguments.product_files, arguments.output_file)
