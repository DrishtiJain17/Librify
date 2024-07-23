import sqlite3
connection = sqlite3.connect("librarydata.db")
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    UserType TEXT CHECK(UserType IN ('Librarian', 'General User')) NOT NULL
);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Sections (
    SectionID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    DateCreated DATE NOT NULL,
    Description TEXT
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    SectionID INTEGER,
    name TEXT NOT NULL,
    Content TEXT,
    Author TEXT,
    DateIssued DATE,
    ReturnDate DATE,
    FOREIGN KEY (SectionID) REFERENCES Sections(SectionID)
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS User_Books (
    IssueID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    BookID INTEGER,
    IssueDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Feedback (
    FeedbackID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    BookID INTEGER,
    FeedbackText TEXT,
    Rating INTEGER CHECK (Rating >= 1 AND Rating <= 5),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS BookRequests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    book_id INTEGER,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);
""")

# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('user1','password1','General User')")
# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('user2','password2','General User')")
# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('user3','password3','General User')")
# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('librarian1','password1','Librarian')")
# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('librarian2','password2','Librarian')")
# cursor.execute("INSERT INTO users(name, password, UserType) VALUES('librarian3','password3','Librarian')")
connection.commit()