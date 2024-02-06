# Humble Bundle Scraper

This is a Python tool designed to scrape bundle data from the Humble Bundle website.

## Modules

- `main.py`: This is the main module of the project. It contains functions for fetching bundle and bundle item data from the Humble Bundle website, and for inserting this data into a SQLite database.

- `database/sqlite_client.py`: This module contains the `SQLiteClient` class, which is used to interact with a SQLite database. It provides methods for connecting to the database, executing queries, and checking if a bundle or bundle item exists in the database. It also provides methods for inserting, updating, and deleting bundles and bundle items in the database.

## Usage

1. Install the required Python packages:

```sh
pip install -r requirements.txt
```

1. Run the main script:

```sh
python main.py
```

This will start the scraper, which will fetch bundle data from the Humble Bundle website and insert it into a SQLite database.

## Note

This project is for educational purposes only. Please respect the terms of service of the Humble Bundle website.

This scraper, as with any other, is liable to break unexpectedly following changes to the structure of Humble Bundle's response structure. Use at your own risk.

## TODO

- Add tests
- Add documentation
- Add typing
