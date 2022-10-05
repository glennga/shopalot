import argparse
import json
import random
import faker

from datagen import utility

# Define the fields that will appear in a Users document.
REQUIRED_FIELDS = ['user_id', 'name']
NULLABLE_FIELDS = []
MISSABLE_FIELDS = ['email', 'phones', 'kids']
ALL_FIELDS = [f for f in set(REQUIRED_FIELDS + NULLABLE_FIELDS + MISSABLE_FIELDS) if '.' not in f]

# Define the **valued** distribution for each field. These must match the fields above.
PET_KINDS = ['cat', 'dog', 'fish', 'bird']
VALUED_DISTRIBUTIONS = {
    # Each value in this dictionary is a function with the Faker data generator as the first argument (f) and the
    # current user record as the second argument (u).

    # A unique 5-digit alphanumeric user ID for each user.
    'user_id': lambda f, u: utility.get_unique_id('user', id_length=5),

    # A phones array is composed of documents that have a phone type, and a phone number. The size of our user phones
    # lists has a binomial distribution with success probability = 0.01.
    'phones': lambda f, u: utility.repeat_and_collect(
        func=lambda: {'kind': random.choice(utility.PHONE_TYPES), 'number': f.phone_number()},
        success_prob=lambda: random.random() > 0.8
    ),

    # A name is a composed of a first and last name.
    'name': lambda f, u: {'first': f.first_name(), 'last': f.last_name()},

    # An email is derived using a user's name.
    'email': lambda f, u: utility.user_name_to_user_email(u['name']['first'], u['name']['last']),

    'kids': lambda f, u: utility.repeat_and_collect(
        func=lambda: { 'name': f.first_name(),
                       'age': random.randint(0, 18),
                       'pets': utility.repeat_and_collect(
                           func=lambda: {'name': f.first_name(), 'kind': random.choice(PET_KINDS)},
                           minimum_times=random.randint(0, 2)
                       )},
        minimum_times=random.randint(0, 4)
    )
}

# Define the missing and null distributions for each field. These must match the fields above. You can use the "."
# notation to specify nested fields.
NULL_DISTRIBUTIONS = {
}
MISSING_DISTRIBUTIONS = {
    # Our email has a 3% chance of being omitted.
    'email': lambda: random.choices([True, False], weights=[0.03, 0.97], k=1)[0],

    # Our phones field has a 3% chance of being omitted.
    'phones': lambda: random.choices([True, False], weights=[0.03, 0.97], k=1)[0],

    'kids': lambda: random.choices([True, False], weights=[0.5, 0.5], k=1)[0]
}


def generate_users(user_count, fake_data_generator, output_file):
    with open(output_file, 'w') as output_fp:
        for _ in range(user_count):
            user_dict = {}

            # The order of the fields matter here! Name must come before email.
            for field in [f for f in ALL_FIELDS if f != 'name' and f != 'email'] + ['name', 'email']:
                user_dict[field] = VALUED_DISTRIBUTIONS[field](fake_data_generator, user_dict)
            utility.insert_missing_or_null(user_dict, NULL_DISTRIBUTIONS, MISSING_DISTRIBUTIONS)
            json.dump(user_dict, output_fp)
            output_fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the Users dataset.')
    parser.add_argument('--user_count', type=int, default=5000, help='Number of users to generate.')
    parser.add_argument('--output_file', default='users.json', help='Location of the output Users dataset.')
    parser.add_argument('--random_seed', default=0, help='Seed used for Faker and the random package.')
    arguments = parser.parse_args()

    # Seed our RNG.
    faker.Faker.seed(arguments.random_seed)
    random.seed(arguments.random_seed)

    # Generate our users.
    generate_users(arguments.user_count, faker.Faker(), arguments.output_file)
