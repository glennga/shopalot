import argparse
import datetime
import json
import os
import random
import time
import decimal

import faker

from datagen import utility

# Define the fields that will appear in a Orders document.
REQUIRED_FIELDS = ['order_id', 'user_id', 'store_id', 'time_placed', 'items', 'total_price']
NULLABLE_FIELDS = ['time_fulfilled', 'pickup_time']
MISSABLE_FIELDS = ['time_fulfilled', 'pickup_time']
ALL_FIELDS = [f for f in set(REQUIRED_FIELDS + NULLABLE_FIELDS + MISSABLE_FIELDS) if '.' not in f]

# Define the **valued** distribution for each field. These must match the fields above.
VALUED_DISTRIBUTIONS = {
    # Each value in this dictionary is a function with all user IDs as the first argument (u), a store ID as the second
    # argument (s), and all product - price pairs associated with that store (p).

    # A unique 5-digit alphanumeric order ID for each order.
    'order_id': lambda u, s, p: utility.get_unique_id('order', id_length=5),

    # The user ID associated with this order. We randomly sample this from the users file.
    'user_id': lambda u, s, p: random.choice(u),

    # The store ID associated with this order. We take this from the stores file.
    'store_id': lambda u, s, p: s,

    # We defer the following to our post processing step.
    'time_placed': lambda u, s, p: 1,
    'time_fulfilled': lambda u, s, p: 1,
    'pickup_time': lambda u, s, p: 1,

    # The items associated with an order. The number of items in an order follows a binomial distribution with p = 0.1.
    'items': lambda u, s, p: utility.repeat_and_collect(
        func=lambda: {**{
            'item_id': utility.get_unique_id('order.item', id_length=5),
            'qty': random.randint(1, 10)
            # Note: prices have a null distribution defined in the utility function below.
        }, **utility.product_to_order_item(random.choice(p))},
        success_prob=lambda: random.random() > 0.8,
        minimum_times=1
    ),

    # The total price associated with an order. This is a derived attribute, and is also handled in the post-processing.
    'total_price': lambda u, s, p: 1
}

# Define the missing and null distributions for each field. These must match the fields above. You can use the "."
# notation to specify nested fields.
NULL_DISTRIBUTIONS = {
    # An order has a 1% chance to not be fulfilled.
    'time_fulfilled': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0],

    # An order has a 1% chance to not be picked up.
    'pickup_time': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
}
MISSING_DISTRIBUTIONS = {
    # An order has a 1% chance to not be fulfilled.
    'time_fulfilled': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0],

    # An order has a 1% chance to not be picked up.
    'pickup_time': lambda: random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
}


def generate_orders(order_count, users_file, stocked_file, products_file, output_file):
    # We store all user IDs and each store's catalog in memory.
    user_ids = list()
    with open(users_file, 'r') as users_fp:
        for user_line in users_fp:
            user_ids.append(json.loads(user_line)['user_id'])
    product_price = {}
    with open(products_file, 'r') as products_fp:
        for products_line in products_fp:
            products_json = json.loads(products_line)
            product_price[products_json['product_id']] = products_json['list_price']
    store_stock_group = {}
    with open(stocked_file, 'r') as stocked_fp:
        for stocked_line in stocked_fp:
            stocked_json = json.loads(stocked_line)
            if stocked_json['store_id'] not in store_stock_group:
                store_stock_group[stocked_json['store_id']] = []
            product_id = stocked_json['product_id']
            product_pair = tuple((product_id, product_price[product_id]))
            store_stock_group[stocked_json['store_id']].append(product_pair)
    del product_price
    store_stock = []
    for k, v in store_stock_group.items():
        store_stock.append(tuple((k, v)))
    del store_stock_group

    with open(output_file, 'w') as output_fp:
        for _ in range(order_count):
            orders_dict = {}
            store_id, product_pairs = random.choice(store_stock)
            for field in ALL_FIELDS:
                orders_dict[field] = VALUED_DISTRIBUTIONS[field](user_ids, store_id, product_pairs)
            utility.insert_missing_or_null(orders_dict, NULL_DISTRIBUTIONS, MISSING_DISTRIBUTIONS)
            json.dump(orders_dict, output_fp)
            output_fp.write('\n')


def enhance_orders(input_file, date_range, growth_intervals, total_count, fake_data_generator, output_file):
    # We define the following to compute the total price attribute (we keep SQL's SUM NULL semantics here).
    def find_total_price(items):
        total_price = decimal.Decimal(0)
        for item in items:
            if item['price'] is not None:
                total_price += decimal.Decimal(item['price'] * item['qty'])
        return float(total_price.quantize(decimal.Decimal('0.01'), decimal.ROUND_HALF_UP))

    # Determine the size of our time intervals.
    growth_delta = datetime.timedelta(days=(date_range[1] - date_range[0]).days / growth_intervals)
    time_increments = []
    work_start = date_range[0]
    for _ in range(growth_intervals):
        work_end = work_start + growth_delta
        time_increments.append({'start': work_start, 'end': work_end})
        work_start = work_end

    # Determine the number of orders placed between each interval.
    # TODO: this part is hard-coded, for now at least.
    group_1_growth_rate = 1.73
    group_2_growth_rate = 3.9
    group_divider = growth_intervals * 0.9
    for i in range(growth_intervals):
        if i < group_divider:
            time_increments[i]['count'] = group_1_growth_rate * i + 1
        else:
            time_increments[i]['count'] = group_2_growth_rate * i + 1
    assert sum(t['count'] for t in time_increments) < total_count

    total_number_of_orders_placed = 0
    with open(input_file, 'r') as input_fp, open(output_file, 'w') as output_fp:
        # Build our growth.
        for i in range(growth_intervals):
            number_of_orders_in_time_period = int(round(time_increments[i]['count']))
            total_number_of_orders_placed = total_number_of_orders_placed + number_of_orders_in_time_period

            generated_datetimes = []
            for _ in range(number_of_orders_in_time_period):
                time_placed = fake_data_generator.date_time_between_dates(
                    datetime_start=time_increments[i]['start'], datetime_end=time_increments[i]['end'])
                pickup_time = fake_data_generator.date_time_between_dates(
                    datetime_start=time_placed, datetime_end=time_placed + datetime.timedelta(hours=6))
                time_fulfilled = fake_data_generator.date_time_between_dates(
                    datetime_start=pickup_time, datetime_end=pickup_time + datetime.timedelta(hours=6))
                generated_datetimes.append({
                    'time_placed': time_placed,
                    'pickup_time': pickup_time,
                    'time_fulfilled': time_fulfilled
                })
            for d in sorted(generated_datetimes, key=lambda a: a['time_placed']):
                line = input_fp.readline()
                order_json = json.loads(line)
                order_json['total_price'] = find_total_price(order_json['items'])
                order_json['time_placed'] = d['time_placed'].isoformat() + '.000Z'
                if 'pickup_time' in order_json:
                    order_json['pickup_time'] = d['pickup_time'].isoformat() + '.000Z'
                order_json['time_fulfilled'] = d['time_fulfilled'].isoformat() + '.000Z'
                output_fp.write(json.dumps(order_json))
                output_fp.write('\n')
                last_datetime = d['time_placed']

        # If we still haven't exhausted all of orders, generate additional times.
        generated_datetimes = []
        while total_number_of_orders_placed < total_count:
            time_placed = fake_data_generator.date_time_between_dates(
                datetime_start=last_datetime, datetime_end=last_datetime + datetime.timedelta(hours=6)
            )
            pickup_time = fake_data_generator.date_time_between_dates(
                datetime_start=time_placed, datetime_end=time_placed + datetime.timedelta(hours=6)
            )
            generated_datetimes.append({
                'time_placed': time_placed,
                'pickup_time': pickup_time
            })
            total_number_of_orders_placed = total_number_of_orders_placed + 1
        for d in sorted(generated_datetimes, key=lambda a: a['time_placed']):
            line = input_fp.readline()
            order_json = json.loads(line)
            order_json['total_price'] = find_total_price(order_json['items'])
            order_json['time_placed'] = d['time_placed'].isoformat() + '.000Z'
            if 'pickup_time' in order_json:
                order_json['pickup_time'] = d['pickup_time'].isoformat() + '.000Z'
            if 'time_fulfilled' in order_json:
                del order_json['time_fulfilled']
            output_fp.write(json.dumps(order_json))
            output_fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the Orders dataset.')
    parser.add_argument('--order_count', type=int, default=20000, help='Number of orders to generate.')
    parser.add_argument('--growth_intervals', default=128, help='Number of intervals to divide growth by.')
    parser.add_argument('--order_start_date', default=datetime.date.fromisoformat('2018-01-01'),
                        type=datetime.date.fromisoformat, help='Start date of orders.')
    parser.add_argument('--order_end_date', default=datetime.date.today(), type=datetime.date.fromisoformat,
                        help='End date of orders.')
    parser.add_argument('--users_file', required=True, help='Location of the input Users dataset.')
    parser.add_argument('--stocked_file', required=True, help='Location of the input StockedBy dataset.')
    parser.add_argument('--products_file', required=True, help='Location of the input Products dataset.')
    parser.add_argument('--output_file', default='orders.json', help='Location of the output Orders dataset.')
    parser.add_argument('--random_seed', default=0, help='Seed used for Faker and the random package.')
    arguments = parser.parse_args()

    # Seed our RNG.
    faker.Faker.seed(arguments.random_seed)
    random.seed(arguments.random_seed)

    # Generate our orders without growth.
    generate_orders(arguments.order_count, arguments.users_file, arguments.stocked_file, arguments.products_file,
                    arguments.output_file + '.tmp')
    time.sleep(5)

    # Add growth to our orders.
    argument_order_interval = [arguments.order_start_date, arguments.order_end_date]
    enhance_orders(arguments.output_file + '.tmp', argument_order_interval, arguments.growth_intervals,
                   arguments.order_count, faker.Faker(), arguments.output_file)
    os.remove(arguments.output_file + '.tmp')
