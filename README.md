# ShopALot Data Generator

## Usage
1. Install `python 3.9` and the package `Faker` (below, we use `virtualenv` to set up our environment).
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Ensure that your `python3` searches the `datagen` directory for modules. Note that this line will have to be run every time you enter a new terminal (you can also choose to export your `datagen` directory in your `.bashrc` file to save some headaches):
```bash
# You should be in the top-level directory, not the 'datagen' directory.
export PYTHONPATH=$PYTHONPATH:$PYTHONPATH:"$(pwd)/datagen"
```

3. Generate the data! 
```bash
python3 datagen/products.py

python3 datagen/stores.py \
  --store_count 400

python3 datagen/users.py \
  --user_count 5000  

python3 datagen/stockedby.py \
  --products_file products.json \
  --stores_file stores.json
  
python3 datagen/orders.py \
  --order_count 20000 \
  --order_start_date 2018-01-01 \
  --users_file users.json \
  --products_file products.json \
  --stocked_file stockedby.json
```

4. For more precise control over the data generator, each script also has a `--help` option:
```bash
> python3 datagen/orders.py --help

usage: orders.py [-h] [--order_count ORDER_COUNT] [--growth_intervals GROWTH_INTERVALS] [--order_start_date ORDER_START_DATE] [--order_end_date ORDER_END_DATE] --users_file USERS_FILE --stocked_file STOCKED_FILE --products_file
                 PRODUCTS_FILE [--output_file OUTPUT_FILE] [--random_seed RANDOM_SEED]

Generate the Orders dataset.

optional arguments:
  -h, --help            show this help message and exit
  --order_count ORDER_COUNT
                        Number of orders to generate.
  --growth_intervals GROWTH_INTERVALS
                        Number of intervals to divide growth by.
  --order_start_date ORDER_START_DATE
                        Start date of orders.
  --order_end_date ORDER_END_DATE
                        End date of orders.
  --users_file USERS_FILE
                        Location of the input Users dataset.
  --stocked_file STOCKED_FILE
                        Location of the input StockedBy dataset.
  --products_file PRODUCTS_FILE
                        Location of the input Products dataset.
  --output_file OUTPUT_FILE
                        Location of the output Orders dataset.
  --random_seed RANDOM_SEED
                        Seed used for Faker and the random package.
```

5. For even more precise control over the data generator, you can edit each script to include your custom fields / distributions.
   1. To include a new field, start by opening the script of the file you want to modify. Add your new field name to the `REQUIRED_FIELDS` array if your field is mandatory, the `NULLABLE_FIELDS` array if your field could be `NULL`, or the `MISSABLE_FIELDS` array if your field could be missing. The last two arrays are not mutually exclusive. If the field to be `NULL` or missing is nested in an object, then use the `.` notation (see the `address.zip_code` in `datagen/stores.py` for an example).
   2. Next, define the distribution your field should follow by including an entry in the `VALUED_DISTRIBUTIONS` dictionary. Your entry should have a key with the field you want to generate, and a function that generates a value. The signature of your function varies depending on which script you are modifying. Note that the `.` notation does **not** apply here, you must build nested objects using the top-level field (see the `name` in `datagen/users.py` for an example).
   3. Finally, if your field is `NULL` or missing, add an entry to the `NULL_DISTRIBUTIONS` and/or `MISSING_DISTRIBUTIONS` dictionary(s). Again, your entry should have a key with the nullable / missable field (the `.` notation applies here) as well as a random function that returns true if a value is `NULL` / missing (otherwise, false).   