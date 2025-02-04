#!/bin/bash

# This script demonstrates the `auto-rest` utility using a SQLite database
# populated with dummy data. The database schema is designed for a blog,
# with tables for authors, posts, and comments. The script populates the
# database and launches an API server using `auto-rest`.

# Define necessary file paths
WORK_DIR=$(dirname "$0")
DEMO_DATA="$WORK_DIR/data.sql"
DB_NAME="$WORK_DIR/blog.db"

if [ -f "$DB_NAME" ]; then

  # Only overwrite existing database with user permission
  read -p "The file '$DB_NAME' already exists. Do you want to replace it? (y/N): " choice
  if [[ "$choice" =~ ^[Yy]$ ]]; then
    rm "$DB_NAME"
    sqlite3 "$DB_NAME" < "$DEMO_DATA"
  fi

else
  sqlite3 "$DB_NAME" < "$DEMO_DATA"
fi

# Launch the API server using auto-rest
auto-rest --sqlite --db-name "$DB_NAME" --app-title "Auto-REST Demo"
