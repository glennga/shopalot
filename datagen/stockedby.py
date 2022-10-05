import argparse
import json
import random
import faker

from datagen import utility

# Define the fields that will appear in a StockedBy document.
REQUIRED_FIELDS = ['product_id', 'store_id', 'qty']
NULLABLE_FIELDS = []
MISSABLE_FIELDS = []
ALL_FIELDS = [f for f in set(REQUIRED_FIELDS + NULLABLE_FIELDS + MISSABLE_FIELDS) if '.' not in f]

# Define the **valued** distribution for each field. These must match the fields above.
VALUED_DISTRIBUTIONS = {
    # Each value in this dictionary is a function with a product doc from the products file (p) and a stores doc from
    # the stores file (s).

    # The product ID associated with this record. We take this from the products file.
    'product_id': lambda p, s: p['product_id'],

    # The store ID associated with this record. We take this from the stores file.
    'store_id': lambda p, s: s['store_id'],

    # The number of items this store has stocked, distributed uniformly between 40 and 100.
    'qty': lambda p, s: random.randint(40, 100)
}

# Define the missing and null distributions for each field. These must match the fields above. You can use the "."
# notation to specify nested fields.
NULL_DISTRIBUTIONS = {
}
MISSING_DISTRIBUTIONS = {
}


def generate_stocked(products_file, stores_file, stocked_prob, output_file):
    with open(output_file, 'w') as output_fp, open(products_file, 'r') as products_fp,\
         open(stores_file, 'r') as stores_fp:
        for store in stores_fp:
            store_json = json.loads(store)
            if 'categories' in store_json:
                store_categories = store_json['categories']
            else:
                store_categories = None
            products_fp.seek(0)
            for product in products_fp:
                product_json = json.loads(product)
                product_category = product_json['category']
                should_product_be_in_store = store_categories is None or product_category in store_categories
                if random.random() < stocked_prob and should_product_be_in_store:
                    stocked_dict = {}
                    for field in ALL_FIELDS:
                        stocked_dict[field] = VALUED_DISTRIBUTIONS[field](product_json, store_json)
                    utility.insert_missing_or_null(stocked_dict, NULL_DISTRIBUTIONS, MISSING_DISTRIBUTIONS)
                    json.dump(stocked_dict, output_fp)
                    output_fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the StockedBy dataset.')
    parser.add_argument('--products_file', required=True, help='Location of the input Products dataset.')
    parser.add_argument('--stores_file', required=True, help='Location of the input Stores dataset.')
    parser.add_argument('--stocked_prob', type=float, default=0.95, help='Probability that a store stocks a product.')
    parser.add_argument('--output_file', default='stockedby.json', help='Location of the output StockedBy dataset.')
    parser.add_argument('--random_seed', default=0, help='Seed used for Faker and the random package.')
    arguments = parser.parse_args()

    # Seed our RNG.
    faker.Faker.seed(arguments.random_seed)
    random.seed(arguments.random_seed)

    # Generate our stockedby.
    generate_stocked(arguments.products_file, arguments.stores_file, arguments.stocked_prob, arguments.output_file)
