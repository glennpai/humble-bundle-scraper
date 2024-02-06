"""
Module for sqlite client
"""

import os
from sqlite3 import connect

class SQLiteClient:
    """
    Class for sqlite client
    """
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = None
        self.connect()

    def connect(self):
        """
        Connect to the database
        """
        self.conn = connect(self.dbname)
        self.execute_query("PRAGMA foreign_keys = ON;")

    def execute_query(self, query, values=None):
        """
        Execute a query on the database
        """
        if self.conn is None:
            self.connect()

        cursor = self.conn.cursor()

        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)

        self.conn.commit()

        return cursor.fetchall()

    def table_exists(self, table_name):
        """
        Check if a table exists in the database
        """
        query = "SELECT * FROM sqlite_master WHERE type='table' AND name=?;"
        values = (table_name)
        result = self.execute_query(query, values)

        return len(result) > 0
    
    def bundle_exists(self, bundle_name):
        """
        Check if a bundle exists in the database
        """
        query = "SELECT * FROM bundle_meta WHERE machine_name=?;"
        values = (bundle_name)
        result = self.execute_query(query, values)

        return len(result) > 0
    
    def insert_bundle(self, bundle):
        """
        Insert a bundle into the database
        """
        query = """
            INSERT INTO bundle_meta (
                machine_name,
                tile_name,
                detailed_marketing_blurb,
                tile_image,
                tile_logo,
                tile_stamp,
                start_date,
                end_date,
                product_url
            ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """
        values = (
            bundle['machine_name'],
            bundle['tile_name'],
            bundle['detailed_marketing_blurb'],
            bundle['tile_image'],
            bundle['tile_logo'],
            bundle['tile_stamp'],
            bundle['start_date'],
            bundle['end_date'],
            bundle['product_url']
        )
        self.execute_query(query, values)

    def delete_bundle(self, bundle_name):
        """
        Delete a bundle from the database
        """
        query = "DELETE FROM bundle_meta WHERE machine_name=?;"
        values = (bundle_name)
        self.execute_query(query, values)

    def update_bundle_price(self, bundle_name, price, msrp_price):
        """
        Update the price of a bundle in the database
        """
        query = "UPDATE bundle_meta SET price=?, msrp_price=? WHERE machine_name=?;"
        values = (price, msrp_price, bundle_name)
        self.execute_query(query, values)

    def bundle_item_exists(self, machine_name, human_name, bundle_name):
        """
        Check if a bundle item exists in the database
        """
        query = "SELECT * FROM bundle_item WHERE machine_name=? AND human_name=? AND bundle_name=?;"
        values = (machine_name, human_name, bundle_name)
        result = self.execute_query(query, values)

        return len(result) > 0

    def insert_bundle_item(self, bundle_item):
        """
        Insert a bundle item into the database
        """
        query = """
            INSERT INTO bundle_item (
                machine_name,
                human_name,
                description_text,
                bundle_name,
                msrp_price
            ) VALUES ( ?, ?, ?, ?, ? );
        """
        values = (
            bundle_item['machine_name'],
            bundle_item['human_name'],
            bundle_item['description_text'],
            bundle_item['bundle_name'],
            bundle_item['msrp_price']
        )
        self.execute_query(query, values)

    def delete_bundle_items(self, bundle_name):
        """
        Delete all bundle items from the database
        """
        query = "DELETE FROM bundle_item WHERE bundle_name=?;"
        values = (bundle_name)
        self.execute_query(query, values)

    def close(self):
        """
        Close the connection to the database
        """
        if self.conn is not None:
            self.conn.close()

        self.conn = None

    def migrate_up(self):
        """
        Migrate the database up
        """
        if not os.path.exists(self.dbname):
            open(self.dbname, "w").close()

        if not self.table_exists("bundle_meta"):
            create_bundle_table_query = """
                CREATE TABLE bundle_meta (
                    machine_name TEXT PRIMARY KEY,
                    tile_name TEXT,
                    detailed_marketing_blurb TEXT,
                    tile_image TEXT,
                    tile_logo TEXT,
                    tile_stamp TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    product_url TEXT,
                    price REAL,
                    msrp_price REAL
                );
            """
            self.execute_query(create_bundle_table_query)

        if not self.table_exists("bundle_item"):
            create_bundle_item_table_query = """
                CREATE TABLE bundle_item (
                    machine_name TEXT,
                    human_name TEXT,
                    description_text TEXT,
                    bundle_name TEXT,
                    msrp_price REAL,
                    FOREIGN KEY (bundle_name) REFERENCES bundle_meta(machine_name),
                    PRIMARY KEY (machine_name, human_name, bundle_name)
                );
            """
            self.execute_query(create_bundle_item_table_query)
