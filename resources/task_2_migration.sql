--changeset adeneuve:1
ALTER TABLE todos
  ADD completed INTEGER(1);

UPDATE todos
SET completed=0;

--changeset adeneuve:2
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password) VALUES
('user1', 'user1'),
('user2', 'user2'),
('user3', 'user3');