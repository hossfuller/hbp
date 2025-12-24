# libhbp

_Revised 4 November 2025_

This is a general python library to do things the way I like them done. This provides utilities for logging, database connections, configuration management, and whatever else I decide to shoe-horn in.

1. [Setting up the virtual environment](#setting_up_the_virtual_environment)
2. [Deploying this library](#deploying_this_library)
    1. [Building](#building)
    1. [Installing and Using](#installing_and_using)
    1. [Updating](#updating)
3. [Usage Examples](#usage_examples)
    1. [ConfigReader](#configreader)
    1. [DatabaseConnector](#databaseconnector)
    1. [PrintLogger](#printlogger)
    1. [SQLiteManager](#sqlitemanager)


<!-- --------------------------------------------------------------------------- -->


<div id='setting_up_the_virtual_environment' />

## Setting up the virtual environment

From start to finish, here's what to do for the different platforms after cloning this repository.


<div id='setup_summary_linux' />

#### Linux

If Debian/Ubuntu:

```sh
sudo apt-get install python3.13 python3.13-venv python3-pip
```

If RHELx:

```sh
sudo apt-get install python3 python3-venv python3-pip
```

Then, for both:

```sh
python3.13 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore ".venv"
pip install -r requirements.txt
```


<div id='setup_summary_windows' />

#### Windows 11

How do you install python on Windows 11?

```sh
python -m venv env
.\env\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore "env"
pip install -r requirements.txt
```

**NOTE:** See that `"env"` on the `--ignore` flag? That may not be necessary for Windows, but if there's a `UnicodeDecodeError` error when running `pipreqs`, you'll need to add that flag to avoid the error.


<!-- --------------------------------------------------------------------------- -->


<div id='deploying_this_library' />

## Deploying this library


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<div id='building' />

### Building

The construction of this module is based on [Python Packaging User Guide](https://packaging.python.org/en/latest/), specifically the [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) page.

First thing is to make sure the `build` thing is installed and updated to latest/greatest.

```sh
python -m pip install --upgrade build
```

Next, in the same directory as the `pyproject.toml` file, run this command:

```sh
python -m build
```

There'll be a lot of text that streams by. Pray there are no errors.


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<div id='installing_and_using' />

### Installing and Using

Super easy:

```sh
python -m pip install path/to/libhbp
```
Obviously replace `path/to/libhbp` to the real on-disk path to this library.


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<div id='updating' />

### Updating

When updating this library, go through the [Building this library](#building_this_library) instructions after making changes. Then, reinstall the library in each respective codebase's directory using the instructions in [Installing and using this library elsewhere](#installing_and_using_this_library_elsewhere).


<!-- --------------------------------------------------------------------------- -->


<div id='usage_examples' />

## Usage Examples

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<div id='configreader' />

### ConfigReader

Establish a `settings.ini` file for your codebase.  Here is an example:

```ini
#----------------------------------------------------------------------------->
# Configuration script for libhbptest application.
#----------------------------------------------------------------------------->

[GENERAL]
csv_dir               = csvs
log_dir               = logs
pickle_dir            = pickles
test_mode             = 0
verbose_output        = 0

[MYSQL]
hostname = 192.168.2.88
database = test_db
username = test_account
password = McFartles
```

Access these configuration settings in code like this:

```python
import argparse
import os

from libhbp.configurator import ConfigReader

def verify_file_path(filepath):
    """
    Checks if a file exists and is a regular file.
    """
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"Error: File '{filepath}' not found.")
    elif not os.path.isfile(filepath):
        raise argparse.ArgumentTypeError(f"Error: '{filepath}' is not a regular file.")
    return filepath

parser = argparse.ArgumentParser(
    description="Quickstart script to test libhbp library."
)
parser.add_argument(
    "-c",
    "--config",
    type=verify_file_path,
    default=DEFAULT_CONFIG_INI_FILE,
    help="Override default config with custom settings file (default: '%(default)s').",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=None,
    help="Enables verbose output.",
)
args = parser.parse_args()

## Read and update configuration
configuration = ConfigReader(args.config)

if args.sleep_time:
    configuration.set("GENERAL", "sleep_time", str(args.sleep_time))

verbose = False
if args.verbose:
    configuration.set("GENERAL", "verbose_output", "1")
    verbose = True
else:
    configuration.set("GENERAL", "verbose_output", "0")

if __name__ == "__main__":
    if verbose:
        print(configuration.get_all())

```

> **NOTE**: Every call to `configuration.get()` must provide a string to the config setting!

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<div id='databaseconnector' />

### DatabaseConnector

Use the `ConfigReader` to store and access the `DatabaseConnector` configuration. Using the same `settings.ini` file above:

```python
from libhbp.configurator import ConfigReader
from libhbp.dbconnector import DatabaseConnector

db_config = {
    "hostname": configuration.get("MYSQL", "hostname"),
    "database": configuration.get("MYSQL", "database"),
    "username": configuration.get("MYSQL", "username"),
    "password": configuration.get("MYSQL", "password"),
}

## Open database connection....
print("Connecting to database...")
db = DatabaseConnector(**db_config)
db.connect()
query_output = db.execute_query("SELECT VERSION();")
print(query_output)
db.disconnect()
```

More usage examples

```python
# Using the class with a context manager
with DatabaseConnection(**db_config) as db:
    if db.connection:
        # Create a table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
        """
        db.execute_query(create_table_query)

        # Insert data
        insert_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        db.execute_query(insert_query, ("Alice", "alice@example.com"))
        db.execute_query(insert_query, ("Bob", "bob@example.com"))

        # Select data
        select_query = "SELECT * FROM users"
        users = db.execute_query(select_query)
        if users:
            print("Users in the database:")
            for user in users:
                print(user)

        # Update data
        update_query = "UPDATE users SET name = %s WHERE id = %s"
        db.execute_query(update_query, ("Alicia", 1))

        # Select updated data
        users_updated = db.execute_query(select_query)
        if users_updated:
            print("Users after update:")
            for user in users_updated:
                print(user)

        # Delete data
        delete_query = "DELETE FROM users WHERE id = %s"
        db.execute_query(delete_query, (2,))

        # Select data after deletion
        users_after_delete = db.execute_query(select_query)
        if users_after_delete:
            print("Users after deletion:")
            for user in users_after_delete:
                print(user)
```


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->



<div id='printlogger' />

### PrintLogger

Use the `ConfigReader` to store and access the `PrintLogger` configuration. Using the same `settings.ini` file above:

```python
from libhbp.configurator import ConfigReader
from libhbp.logger import PrintLogger

## Command line parsing
parser = argparse.ArgumentParser(
    description="Quickstart script to test libhbp library."
)
parser.add_argument(
    "-n",
    "--nolog",
    action="store_true",
    default=None,
    help="Disable logging.",
)
args = parser.parse_args()

## Read and update configuration
configuration = ConfigReader(args.config)

## Set up logging
if not args.nolog:
    sys.stdout = PrintLogger(
        configuration.get("GENERAL", "log_dir"),
    )
```

From here, unless the `-n` flag is given, logs will be created for this script and written to whatever the `log_dir` is set to.


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->



<div id='sqlitemanager' />

### SQLiteManager

Currently hard-coded only for HBP data. Doesn't rely on the `ConfigReader` for anything right now, but you may want to insert stuff into your `settings.ini` just in case the day does come when `SQLiteManager` does call upon `ConfigReader`'s services.

Example usage:

```python
from libhbp.sqlitemgr import SQLiteManager

db_dir      = config.get("paths", "db_dir")
db_filename = config.get("database", "hbp_db_filename")
db_table    = config.get("database", "hbp_table")
db_file_path = Path(db_dir, db_filename)
print(f"Writing to {db_table} to file '{db_file_path}'.")

with SQLiteManager(db_filename) as db: 
    db.insert_hbpdata(str(uuid.uuid4()), 111111, 222222, 333333, 86.7, 3.14, 6.28)
    db.insert_hbpdata(str(uuid.uuid4()), 444444, 555555, 666666, 92.1, 14.5, 9.01)
    db.insert_hbpdata(str(uuid.uuid4()), 777777, 888888, 999999, 95.5, 7.77, 19.77)

    all_data = db.read_hbpdata_all()
    print("All data:")
    pprint.pprint(all_data)
    print()

    select_data = db.get_hbpdata_data(
        f"SELECT * FROM {db_table} WHERE game_pk = ?",
        [444444]
    )
    print("Just some of the data:")
    pprint.pprint(select_data)
```