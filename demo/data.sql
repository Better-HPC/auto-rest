-- Create users table (formerly authors) with status field
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'active'
);

-- Create posts table
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Create comments table with composite primary key
CREATE TABLE comments (
  post_id INTEGER,
  author_id INTEGER,
  author_name TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (post_id, author_id),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Insert dummy data into users table
INSERT INTO users (first_name, last_name, email) VALUES
  ('John', 'Doe', 'john.doe@example.com'),
  ('Jane', 'Smith', 'jane.smith@example.com'),
  ('Alice', 'Johnson', 'alice.johnson@example.com');

-- Insert dummy data into posts table
INSERT INTO posts (author_id, title, content) VALUES
  (1, 'My First SQL Query', 'This is an introduction to writing your first SQL query.'),
  (2, 'SQL Joins Explained', 'Learn how to combine data from multiple tables using SQL joins.'),
  (3, 'Learning SQLite', 'SQLite is a great tool for small applications, and its perfect for embedded systems.');

-- Insert dummy data into comments table
INSERT INTO comments (post_id, author_id, author_name, content) VALUES
  (1, 1, 'Tom', 'Great explanation on basic SQL queries!'),
  (2, 2, 'Emily', 'SQL joins were always confusing to me, this makes it much clearer.'),
  (3, 3, 'David', 'SQLite is amazing for small-scale projects, love this post.'),
  (3, 1, 'Sarah', 'Constraints are vital in database design, thanks for the insights!'),
  (2, 3, 'Mark', 'The advanced query tips will definitely help with my performance issues.');
