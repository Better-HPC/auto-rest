#!/bin/bash

# This script demonstrates the `auto-rest` utility using a SQLite database
# populated with dummy data. The database schema is designed for a blog,
# with tables for authors, posts, and comments. The script populates the
# database and launches an API server using `auto-rest`.

# Define database file
DB_NAME="${1:-demo.db}"

# Check if the database already exists
if [ -f "$DB_NAME" ]; then
  read -p "The file '$DB_NAME' already exists. Do you want to replace it? (y/N): " choice
  if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    rm "$DB_NAME"
    sqlite3 "$DB_NAME" < data.sql
  fi
fi

# Launch the API server using auto-rest
auto-rest --enable-docs --enable-write --sqlite --db-name "$DB_NAME" --app-title "Auto-REST Demo"
