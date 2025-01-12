#!/bin/bash

# This script demonstrates the `auto-rest` utility using a SQLite database
# populated with dummy data. The database schema is designed for a blog,
# with tables for authors, posts, and comments. The script populates the
# database and launches an API server using `auto-rest`.

# Define database file
DB_NAME="${1:-demo.db}"

# Check if the database already exists
if [ -f "$DB_NAME" ]; then
  rm "$DB_NAME"
fi

# Run the SQL commands in batch mode to create tables and insert data
sqlite3 "$DB_NAME" <<EOF
  -- Create authors table
  CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
  );

  -- Create posts table
  CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(id)
  );

  -- Create comments table
  CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
  );

  -- Insert dummy data into authors table
  INSERT INTO authors (first_name, last_name, email) VALUES
    ('John', 'Doe', 'john.doe@example.com'),
    ('Jane', 'Smith', 'jane.smith@example.com'),
    ('Alice', 'Johnson', 'alice.johnson@example.com');

    -- Insert dummy data into posts table
  INSERT INTO posts (author_id, title, content) VALUES
    (1, 'My First SQL Query', 'This is an introduction to writing your first SQL query.'),
    (2, 'SQL Joins Explained', 'Learn how to combine data from multiple tables using SQL joins.'),
    (3, 'Learning SQLite', 'SQLite is a great tool for small applications, and its perfect for embedded systems.');

    -- Insert dummy data into comments table
  INSERT INTO comments (post_id, author_name, content) VALUES
    (1, 'Tom', 'Great explanation on basic SQL queries!'),
    (2, 'Emily', 'SQL joins were always confusing to me, this makes it much clearer.'),
    (3, 'David', 'SQLite is amazing for small-scale projects, love this post.'),
    (4, 'Sarah', 'Constraints are vital in database design, thanks for the insights!'),
    (5, 'Mark', 'The advanced query tips will definitely help with my performance issues.');
EOF

auto-rest --enable-docs --enable-meta --enable-version --enable-write --sqlite --db-name demo.db
