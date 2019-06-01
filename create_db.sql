CREATE TABLE IF NOT EXISTS Deck(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY(parent_id) REFERENCES Deck(id)
);

CREATE TABLE IF NOT EXISTS Card(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    EF REAL NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    due INTEGER NOT NULL,
    last_interval INTEGER,
    deck_id INTEGER,
    FOREIGN KEY(deck_id) REFERENCES Deck(id)
);

INSERT INTO deck (name, parent_id) VALUES ('prog-langs', NULL);
INSERT INTO deck (name, parent_id) VALUES ('Python', 1);
INSERT INTO deck (name, parent_id) VALUES ('C', 1);

INSERT INTO card (front, back, ef, due, last_interval, deck_id) VALUES
('general question 1', 'general answer 1', 2.5, 12345, 6, 1);

INSERT INTO card (front, back, ef, due, last_interval, deck_id) VALUES
('general question 2', 'general answer 2', 2.5, 10000, 54, 1);

INSERT INTO card (front, back, ef, due, last_interval, deck_id) VALUES
('Python question 1', 'Python answer 1', 1.5, 6542, 98, 2);

INSERT INTO card (front, back, ef, due, last_interval, deck_id) VALUES
('Python question 2', 'Python answer 2', 1.5, 6542, 98, 2);

INSERT INTO card (front, back, ef, due, last_interval, deck_id) VALUES
('C question 1', 'C answer 1', 1.2, 6542, 98, 2);