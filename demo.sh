#!/bin/bash

# This script demonstrates the `auto-rest` utility using a SQLite database
# populated with dummy data pulled from the application test suite.

DB_NAME="demo.db"
SQL_FILE="tests/fixtures.sql"

# Check if the fixtures file exists
if [ ! -f "$SQL_FILE" ]; then
  echo "Error: Fixtures file '$SQL_FILE' not found. Please ensure the file exists."
  exit 1
fi

# Check if the database already exists
if [ ! -f "$DB_NAME" ]; then
  echo "Example database '$DB_NAME' not found. Creating it..."
  sqlite3 "$DB_NAME" < "$SQL_FILE"
fi

# Launch the API server
auto-rest --enable-meta --sqlite --db-host /demo.db
