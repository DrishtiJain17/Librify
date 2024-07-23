**Librify (Library Management System)** made for **App Dev-I** as a part of **IITM BS degree program**.

**Introduction:**

Librify is an online library management system that tracks which e-books are available, who
has borrowed them, and when the e-books are due for return. It also helps users find and
request books. It keeps records of library users and manages tasks like adding new books to a
section or removing old ones. Librarians can add books to various sections which can be
created, and deleted, and the section information can be edited. It is a multi-user application
where users can request and read e-books, mark them as complete, and return the e-books.
The librarians can issue, revoke, add e-books and sections, add e-books to sections, and
monitor the status of an e-book and the user it is issued to.

**Models:**
1. User Model:
  - A User includes attributes: Username, Password, User ID, and User type. UserType
can be either ‘General User’ or ‘Librarian’. The credentials are checked accordingly,
and the corresponding dashboard is shown after successfully logging in.
  - General Users can Browse and search sections and e-books (using the functional
search bar in the navigation bar). They can also request books and withdraw these
requests. Users can read books present in their dashboard (issued by one of the
librarians), mark the book as complete, and give feedback for a book (all reviews and
ratings are stored in the database along with other information).
  - Librarians can search for sections (using the functional search bar), add, edit, delete,
and view the sections. They are also capable of performing the same functions on
books.
  - Librarians can manage book requests (under the ‘Book Requests’ tab) by granting or
rejecting them. They can also revoke access to a book otherwise, the book
automatically gets revoked after 7 days of being issued to a user. They can also see all
the previously “managed” book requests whether they were ‘issued’, ‘rejected’, or
‘revoked’.
  - Both Librarians and General Users can log out, which clears the current session, and
they would need to log in again to access their respective dashboards.

2. Book Model:
  - A Book has the following attributes: Book ID, Section ID (ID of the section to which
the book belongs), title, author of the book, and its content.
  - Each book is assigned a section, and its section ID is present in the Books table to
relate it to other tables, like sections table, feedback table, book requests, etc.

3. Book Request Model:
  - Book Requests include attributes like the User ID of the user who requested the book,
request date, return date, the status of the book request, and book ID along with the
section ID for the book. It relates to the user and book models to manage book
borrowing as all the book requests are shown on the librarian's dashboard after a user
has requested a book. A librarian may grant or reject the request according to which
the book may or may not be accessible to the user.

4. The book request status decides whether a user can access the book. The status of a
book request might be ‘pending’, ‘issued’, ‘revoked’, or ‘rejected’. All Book Requests
with any of the statuses are shown on the librarian’s dashboard under different
headings, such as ‘Manage book requests’, ‘Issued Books’(Books can be revoked in
this section), and ‘Other Book Requests’.


**Overall System Design:**
1. Frontend Design:
  - The frontend design was created using Flask, Jinja2 templates, CSS and Bootstrap.
  - Simplified design, and Properly designed login forms, navigation bars, cards, buttons,
search bars, etc. , in the user and librarian dashboards, make it easy for users and
librarians to use, and navigate efficiently through the Flask app.

2. Backend Design:
  - The backend design was created using Python, and SQLite3.
  - All the data under the models: Book Requests, Sections, Books, Users, and Feedback,
User Books, is stored in the SQLite3 database.
  - Corresponding Python functions are called when data is to be entered, retrieved,
updated, or deleted, i.e., all the necessary CRUD operations for the library
management system are done by Python functions. Various Flask routes are assigned
to these Python functions.

3. Functionality Implementation:
  - The library management system implements all the core functionalities including user
registration and authentication, book and section management, searching and
browsing books and sections, accessing book content only for some allotted time(for
general users), book request management, and user feedback management.
  - User authentication is performed by retrieving data from the database and matching
the entered credentials. If the credentials match, the dashboard is shown, and If the
credentials entered don’t match any row in the database, a suitable message is
displayed. The same functionality is used for implementing search functionality.
Conclusion: The Librify project provides an effective solution for managing library
resources and enhancing user experience. By integrating user-friendly design and robust
functionality, Librify aims to streamline library operations and improve accessibility to books
for users.
