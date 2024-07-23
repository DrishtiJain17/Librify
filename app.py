from flask import Flask, render_template, request, redirect, url_for, session,flash
import sqlite3
from datetime import datetime,timedelta
app = Flask(__name__)
app.debug=True
app.secret_key = "2fh5kd4nl"
@app.route("/" , methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/userlogin.html",methods=['GET','POST'])
def userlogin():
    if request.method =='POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        name = request.form['name']
        password = request.form['password']
        print(name,password)
        cursor.execute("SELECT name,password FROM users where UserType='General User' and name='"+name+"' and password = '"+password+"'")
        results = cursor.fetchall()
        if len(results)==0:
            message = "Wrong Credentials, try again"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('userlogin'))
        else :
            cursor.execute("SELECT UserID FROM users where UserType='General User' and name='"+name+"' and password = '"+password+"'")
            session["user_id"]= cursor.fetchone()[0]
            session["logged_in"] = True
            print(session)
            connec.close()
            return redirect(url_for("user_books",user_id=session["user_id"]))
    return render_template("userlogin.html") 

@app.route('/userdash.html/<int:user_id>')
def user_books(user_id):
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    results=cursor.execute("SELECT name FROM users WHERE UserID=? AND UserType='General User' ",(user_id,)).fetchone()
    if results==None:
            message = "Wrong Credentials, try again"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('userlogin'))
    name=results[0]
    return_date=cursor.execute("SELECT return_date FROM BookRequests WHERE status='issued' AND user_id=?",(user_id,)).fetchone()
    if return_date is not None:
        return_date=return_date[0]
        return_date = datetime.strptime(return_date, '%Y-%m-%d %H:%M:%S.%f')
        diff = return_date - datetime.now()
        days_left = diff.days
    else:
        days_left = 0
    if days_left==0:
        cursor.execute("DELETE FROM User_Books WHERE UserID=? AND DueDate=?",(user_id,return_date))
        cursor.execute("UPDATE BookRequests SET status='revoked' WHERE user_id=? AND return_date=?",(user_id,return_date))
    userbooksinfo = cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.id,u.UserID
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE (br.status='issued'
        AND ?>0
        AND br.user_id=?)
    """,(days_left,user_id,)).fetchall()
    requested_booksinfo = cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status,br.id
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE (br.status='pending'
        AND br.user_id=?)
    """,(user_id,)).fetchall()
    other_requests=cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE ((br.status='rejected'
        OR br.status='revoked'
        OR br.status='returned')
        AND br.user_id=?)""",(user_id,)).fetchall()
    connec.close()
    return render_template("userdash.html",userbooksinfo=userbooksinfo,requested_booksinfo=requested_booksinfo,other_requests=other_requests,name=name,user_id=user_id)

@app.route("/librarianlogin.html", methods=['GET','POST'])
def librarianlogin():
    if request.method =='POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        name = request.form['name']
        password = request.form['password']
        print(name,password)
        cursor.execute("SELECT name,password FROM users where UserType='Librarian' and name='"+name+"' and password = '"+password+"'")
        results = cursor.fetchall()
        if len(results)==0:
            message = "Wrong Credentials, try again"
            flash(message,"info")
            #return render_template("error.html",message=message)
            return redirect(url_for('librarianlogin'))
        else :
            
            cursor.execute("SELECT UserID FROM users where UserType='Librarian' and name='"+name+"' and password = '"+password+"'")
            session["user_id"]= cursor.fetchone()[0]
            session["logged_in"] = True
            print(session)
            connec.close()
            user_id=session.get('user_id')
            return redirect(url_for('libdash',user_id=user_id))
    return render_template("librarianlogin.html")

@app.route('/libdash/<int:user_id>',methods=['GET','POST'])
def libdash(user_id):
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        cursor.execute("SELECT * FROM Sections")
        Sections = cursor.fetchall()
        name=cursor.execute("SELECT name FROM users WHERE UserID=? AND  UserType='Librarian'",(user_id,)).fetchone()
        if name is None:
            message = "Wrong Credentials, try again"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('librarianlogin'))           
        return render_template("libdash.html",name=name[0],Sections=Sections,user_id=user_id)

@app.route('/searchsections',methods = ['GET','POST'])
def search_sections():
    section_value = request.form['search']
    has_searched=True
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    search_results = cursor.execute("SELECT * FROM Sections WHERE (SectionID LIKE ? OR name LIKE ? OR DateCreated LIKE ? OR Description LIKE ? )",('%'+section_value+'%','%'+section_value+'%','%'+section_value+'%','%'+section_value+'%')).fetchall()
    user_id = session.get('user_id')
    name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    Sections=cursor.execute("SELECT * FROM Sections")
    if section_value=='':
        search_results=[]
    return render_template('libdash.html',has_searched=has_searched,search_results=search_results,Sections=Sections,name=name)

@app.route('/searchsectionsuser',methods = ['GET','POST'])
def search_sectionsuser():
    section_value = request.form['search']
    has_searched=True
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    search_results = cursor.execute("SELECT * FROM Sections WHERE (SectionID LIKE ? OR name LIKE ? OR DateCreated LIKE ? OR Description LIKE ? )",('%'+section_value+'%','%'+section_value+'%','%'+section_value+'%','%'+section_value+'%')).fetchall()
    user_id = session.get('user_id')
    name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    Sectionsinfo=cursor.execute("SELECT * FROM Sections")
    if section_value=='':
        search_results=[]
    return render_template('browsebooks.html',has_searched=has_searched,search_results=search_results,Sectionsinfo=Sectionsinfo,name=name,user_id=user_id)

@app.route('/searchbooks',methods = ['GET','POST'])
def search_books():
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    book_value = request.form['search']
    has_searched=True
    search_results = cursor.execute("SELECT * FROM Books WHERE (BookID LIKE ? OR name LIKE ? OR Author LIKE ? )",('%'+book_value+'%','%'+book_value+'%','%'+book_value+'%')).fetchall()
    user_id = session.get('user_id')
    user_type=cursor.execute("SELECT UserType FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    Booksinfo=cursor.execute("SELECT * FROM Books").fetchall()
    if user_type=='Librarian':
        return render_template('viewbookslib.html',has_searched=has_searched,search_results=search_results,Booksinfo=Booksinfo,name=name,book_value=book_value,user_id=user_id)
    return render_template('viewbooks.html',has_searched=has_searched,search_results=search_results,Booksinfo=Booksinfo,name=name,user_id=user_id)


@app.route("/signup.html", methods=['GET','POST'])
def signup():
    if request.method =='POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        name = request.form['name']
        password = request.form['password']
        if name=='' or password=='':
            message="name and password should not be empty"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('signup'))
        print(name , password)
        cursor.execute("INSERT INTO users (name,password,UserType) VALUES (?,?,'General User')", (name , password))
        connec.commit()
        connec.close()
    return render_template("signup.html")

@app.route("/newsection.html", methods=['GET','POST'])
def newsection():
    user_id=session.get('user_id')
    if request.method =='POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        name = request.form['name']
        name=name.upper()
        datecreated = request.form['date']
        description = request.form['description']
        print(name ,datecreated, description)
        if name=='' or datecreated=='' or description=='':
            message="Please fill all details of the section"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('newsection'))
        cursor.execute("INSERT INTO Sections (name,DateCreated,Description) VALUES (?,?,?)", (name , datecreated,description))
        connec.commit()
        return redirect(url_for('libdash',user_id=user_id))
    return render_template("newsection.html",user_id=user_id)

@app.route("/addbooktosection.html", methods=['GET','POST'])
def addbooktosection():
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    user_id=session.get('user_id')
    if request.method =='POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        name = request.form['name']
        author = request.form['author']
        content = request.form['content']
        SectionName = request.form['Section']
        # uname=cursor.execute("SELECT name FROM users WHERE UserID=? AND UserType='Librarian'",(user_id,)).fetchone()[0]
        if name=='' or author=='' or content=='' or SectionName=='':
            message="Please fill all details of the book"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('addbooktosection'))
        cursor.execute("INSERT INTO Books (name,Author,Content, SectionID) VALUES (?,?,?,(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"'))", (name , author,content))
        Sectioninfo=cursor.execute("SELECT name FROM Sections").fetchall()
        # Sections=cursor.execute("SELECT * FROM Sections").fetchall()
        connec.commit()
        connec.close()
        return redirect(url_for('libdash',user_id=user_id))
    Sectioninfo=cursor.execute("SELECT name FROM Sections").fetchall()
    connec.close()
    return render_template("addbooktosection.html",Sectioninfo=Sectioninfo,user_id=user_id)

@app.route("/viewsection.html",methods=['GET','POST'])
def viewsection():
    user_id=session.get('user_id')
    if request.method == 'POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        SectionName=request.form['section']
        cursor.execute("SELECT * FROM Sections WHERE SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')")
        Sectioninfo = cursor.fetchall()
        cursor.execute("SELECT b.BookID, b.name, b.Author, b.Content FROM Books b WHERE b.SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')")
        Booksinfo = cursor.fetchall()
        connec.close()
        print(SectionName)
    return render_template("viewsection.html",Sectioninfo=Sectioninfo,Booksinfo=Booksinfo,user_id=user_id)

@app.route("/editsection/<int:section_id>", methods=['GET','POST'])
def editsection(section_id):
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    Sectioninfo = cursor.execute("SELECT * FROM Sections WHERE SectionID=?", (section_id,)).fetchall()
    user_id = session.get('user_id')
    name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    if request.method =='POST':
        sectionname=request.form['section']
        datecreated=request.form['date']
        description=request.form['description']
        cursor.execute("UPDATE Sections SET name=? WHERE SectionID=?", (sectionname ,section_id))
        cursor.execute("UPDATE Sections SET DateCreated=? WHERE SectionID=?", (datecreated ,section_id))
        cursor.execute("UPDATE Sections SET Description=? WHERE SectionID=?", (description ,section_id))
        Sections=cursor.execute("SELECT * FROM Sections")
        connec.commit()
        return redirect(url_for('libdash',user_id=user_id))
    connec.close()
    return render_template("editsection.html",Sectioninfo=Sectioninfo,user_id=user_id)

@app.route("/editbook/<int:book_id>", methods=['GET','POST'])
def editbook(book_id):
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    Bookinfo = cursor.execute("SELECT * FROM Books WHERE BookID=?", (book_id,)).fetchall()
    user_id = session.get('user_id')
    # name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    Sections=cursor.execute("SELECT * FROM Sections").fetchall()
    if request.method =='POST':
        bookname=request.form['book']
        content=request.form['content']
        author=request.form['author']
        sectionname=request.form['section']
        section_id=cursor.execute("SELECT SectionID FROM Sections WHERE name=?",(sectionname,)).fetchone()[0]
        cursor.execute("UPDATE Books SET name=? WHERE BookID=?", (bookname ,book_id))
        cursor.execute("UPDATE Books SET Content=? WHERE SectionID=?", (content ,book_id))
        cursor.execute("UPDATE Books SET Author =? WHERE SectionID=?", (author ,book_id))
        cursor.execute("UPDATE Books SET SectionID=? WHERE BookID=?",(section_id,book_id))
        connec.commit()
        return redirect(url_for('libdash',user_id=user_id))
    connec.close()
    return render_template("editbook.html",Bookinfo=Bookinfo,Sections=Sections,user_id=user_id)

@app.route("/deletesection",methods=['GET','POST'])
def deletesection():
    if request.method == 'POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        SectionName=request.form['section']
        section_id=cursor.execute("SELECT SectionID FROM Sections WHERE name=?",(SectionName,)).fetchone()[0]
        book_id=cursor.execute("SELECT BookID FROM Books WHERE SectionID=?",(section_id,)).fetchall()
        cursor.execute("DELETE FROM Sections WHERE SectionID=?",(section_id,))
        cursor.execute("DELETE FROM Books WHERE SectionID=?",(section_id,))
        for i in range(len(book_id)):
            cursor.execute("DELETE FROM User_Books WHERE BookID=?",(book_id[i][0],))
            cursor.execute("DELETE FROM BookRequests WHERE book_id=?",(book_id[i][0],))
            cursor.execute("DELETE FROM Feedback WHERE BookID=?",(book_id[i][0],))
    user_id = session.get('user_id')
    # name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    # Sections=cursor.execute("SELECT * FROM Sections")
    connec.commit()
    return redirect(url_for('libdash',user_id=user_id))


@app.route("/deletebook",methods=['GET','POST'])
def deletebook():
    if request.method == 'POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        book_id=request.form['book']
    SectionName=cursor.execute("SELECT name FROM Sections WHERE SectionID=(SELECT SectionID FROM Books WHERE BookID=?)",(book_id,)).fetchone()[0]
    cursor.execute("DELETE FROM BookRequests WHERE book_id=?",(book_id,))
    cursor.execute("DELETE FROM User_Books WHERE BookID=?",(book_id,))        
    cursor.execute("DELETE FROM Feedback WHERE BookID=?",(book_id,))
    cursor.execute("DELETE FROM Books WHERE BookID=?",(book_id,))
    user_id = session.get('user_id')
    name=cursor.execute("SELECT name FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
    Sectioninfo=cursor.execute("SELECT * FROM Sections WHERE SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')").fetchall()
    Booksinfo=cursor.execute("SELECT b.BookID, b.name, b.Author, b.Content FROM Books b WHERE b.SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')").fetchall()
    connec.commit()
    connec.close()
    return render_template('viewsection.html',Sectioninfo=Sectioninfo,Booksinfo=Booksinfo,name=name)

@app.route("/viewsectionuser.html",methods=['GET','POST'])
def viewsectionuser():
    if request.method == 'POST':
        connec = sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        SectionName=request.form['section']
        cursor.execute("SELECT SectionID, name, Description, DateCreated FROM Sections WHERE SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')")
        Sectioninfo = cursor.fetchall()
        cursor.execute("SELECT b.BookID, b.name, b.Author, b.Content FROM Books b WHERE b.SectionID=(SELECT SectionID FROM Sections WHERE name = '"+SectionName+"')")
        Booksinfo = cursor.fetchall()
        connec.close()
    return render_template("viewsectionuser.html",Sectioninfo=Sectioninfo,Booksinfo=Booksinfo)

@app.route('/readbook.html/<int:book_id>', methods=['GET','POST'])
def read_book(book_id):
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    bookdetails = cursor.execute("SELECT b.Content, b.name, b.Author FROM Books b WHERE b.BookID = ?",(book_id,)).fetchone()
    connec.close()
    return render_template("readbook.html",content=bookdetails[0],Bookname=bookdetails[1],author=bookdetails[2],bookid=book_id)


@app.route("/viewbooks.html",methods=['GET','POST'])
def viewbooks():
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("SELECT * FROM Books b")
    Booksinfo = cursor.fetchall()
    connec.close()
    return render_template("viewbooks.html",Booksinfo=Booksinfo)

@app.route("/viewbookslib.html",methods=['GET','POST'])
def viewbookslib():
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("SELECT * FROM Books b")
    Booksinfo = cursor.fetchall()
    connec.close()
    user_id=session.get('user_id')
    return render_template("viewbookslib.html",Booksinfo=Booksinfo,user_id=user_id)

@app.route("/browsebooks.html",methods=['GET','POST'])
def browsebooks():
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("SELECT * FROM Sections s")
    user_id=session.get('user_id')
    Sectionsinfo = cursor.fetchall()
    connec.close()
    return render_template("browsebooks.html",Sectionsinfo=Sectionsinfo,user_id=user_id)

def checkmaxrequests(user_id):
    connec = sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("SELECT COUNT(*) FROM BookRequests WHERE user_id = ? AND (status='issued' OR status='pending')",(user_id,))
    numofrequests = cursor.fetchone()[0]
    connec.close()
    return numofrequests >= 5

@app.route('/request-book/<int:book_id>', methods=['GET','POST'])
def request_book(book_id):
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    user_id = session.get('user_id')
    if not user_id:
        message = "You were logged out. Please login again to request a book."
        flash(message,"info")
        # return render_template('error.html',message=message)
        return redirect(url_for('index'))

    elif checkmaxrequests(user_id):
        message= 'You have reached the maximum limit of book requests (5).'
        flash(message,"info")
        # return render_template('error.html',message=message)
        return redirect(url_for('browsebooks'))

    if request.method == 'GET':
        access_days =7
        return_date = datetime.now() + timedelta(days= access_days)
        connec =sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        user_type=cursor.execute("SELECT UserType FROM users WHERE UserID=?",(user_id,)).fetchone()[0]
        if user_type=='General User':
            cursor.execute("INSERT INTO BookRequests (user_id,book_id,return_date,status,request_date) VALUES (?,?,?,?,?)",(user_id, book_id, return_date, 'pending',datetime.now()))
            connec.commit()
            connec.close()
        else:
            message="You are logged in as a librarian. Librarians cannot request for books"
            flash(message,"info")
            # return render_template('error.html',message=message)
            return redirect(url_for('browsebooks'))
        message= 'Your book request has been submitted successfully!'
        flash(message,"info")
        # return render_template('error.html',message=message)
        return redirect(url_for('browsebooks'))

@app.route('/book-requested.html')
def book_requested():
    return render_template('book_requested.html')

@app.route('/bookrequests.html')
def book_requests():
        connec =sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        user_id=session.get('user_id')
        return_date=cursor.execute("SELECT return_date FROM BookRequests WHERE status='issued' AND user_id=?",(user_id,)).fetchone()
        if return_date is not None:
            return_date=return_date[0]
            return_date = datetime.strptime(return_date, '%Y-%m-%d %H:%M:%S.%f')
            diff = return_date - datetime.now()
            days_left = diff.days
        else:
            days_left = 0
        pendingrequests = cursor.execute("""
        SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE br.status='pending'
    """).fetchall()
        issuedrequests = cursor.execute("""
        SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE (br.status='issued'
        AND ?>0)
    """,(days_left,)).fetchall()
        returned_requests=cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status,br.id
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE br.status='returned'
    """).fetchall()
        connec.close()
        return render_template("bookrequests.html",pendingrequests=pendingrequests,issuedrequests=issuedrequests,returned_requests=returned_requests,user_id=user_id)

@app.route('/grant/<int:request_id>', methods=['GET','POST'])
def grant(request_id):
    l_user_id=session.get('user_id')
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    return_date = cursor.execute("SELECT return_date FROM BookRequests WHERE id=?",(request_id,)).fetchall()[0][0]
    user_id= cursor.execute("SELECT user_id FROM BookRequests WHERE id=?",(request_id,)).fetchall()[0][0]
    book_id= cursor.execute("SELECT book_id FROM BookRequests WHERE id=?",(request_id,)).fetchall()[0][0]
    cursor.execute("UPDATE BookRequests SET status='issued' WHERE id=?",(request_id,))
    cursor.execute("INSERT INTO User_Books (UserID,BookID,DueDate,IssueDate) VALUES (?,?,?,?)",(user_id, book_id, return_date,datetime.now()))
    pendingrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status        
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='pending'
    """).fetchall()
    issuedrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='issued'
    """).fetchall()
    returned_requests=cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status,br.id
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE br.status='returned'
    """).fetchall()
    connec.commit()
    connec.close()
    return render_template('bookrequests.html',pendingrequests=pendingrequests,issuedrequests=issuedrequests,returned_requests=returned_requests,user_id=l_user_id)

@app.route('/reject/<int:request_id>', methods=['GET','POST'])
def reject(request_id):
    user_id=session.get('user_id')
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("UPDATE BookRequests SET status='rejected' WHERE id=?",(request_id,))
    pendingrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status        
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='pending'
    """).fetchall()
    issuedrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='issued'
    """).fetchall()
    returned_requests=cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status,br.id
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE br.status='returned'
    """).fetchall()
    connec.commit()
    connec.close()
    return render_template('bookrequests.html',pendingrequests=pendingrequests,issuedrequests=issuedrequests,returned_requests=returned_requests,user_id=user_id)

@app.route('/revoke/<int:request_id>', methods=['GET','POST'])
def revoke(request_id):
    user_id=session.get('user_id')
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    cursor.execute("UPDATE BookRequests SET status='revoked' WHERE id=?",(request_id,))
    pendingrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status        
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='pending'
    """).fetchall()
    issuedrequests = cursor.execute("""
    SELECT br.id, u.name AS username, b.name AS bookname, b.author, br.request_date, br.return_date, br.status
    FROM BookRequests br
    INNER JOIN Users u ON br.user_id = u.UserID
    INNER JOIN Books b ON br.book_id = b.BookID
    WHERE br.status='issued'
    """).fetchall()
    returned_requests=cursor.execute("""
        SELECT b.BookID, b.name, b.Author, br.request_date, br.return_date, u.name,br.status,br.id
        FROM BookRequests br
        INNER JOIN Users u ON br.user_id = u.UserID
        INNER JOIN Books b ON br.book_id = b.BookID
        WHERE br.status='returned'
    """).fetchall()
    connec.commit()
    connec.close()
    return render_template('bookrequests.html',pendingrequests=pendingrequests,issuedrequests=issuedrequests,returned_requests=returned_requests,user_id=user_id)

@app.route('/withdraw_request/<int:request_id>', methods=['GET','POST'])
def withdraw_request(request_id):
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    user_id=cursor.execute("SELECT user_id FROM BookRequests WHERE id=?",(request_id,)).fetchone()[0]
    cursor.execute("DELETE FROM BookRequests WHERE id=? AND status='pending'",(request_id,))
    connec.commit()
    connec.close()
    return redirect(url_for('user_books',user_id=user_id))

@app.route('/markascompleted/<int:request_id>', methods=['GET','POST'])
def markascompleted(request_id):
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    user_id=cursor.execute("SELECT user_id FROM BookRequests WHERE id=?",(request_id,)).fetchone()[0]
    book_id=cursor.execute("SELECT book_id FROM BookRequests WHERE id=?",(request_id,)).fetchone()[0]
    cursor.execute("UPDATE User_Books SET Status='completed' WHERE (UserID=? AND BookID=?)",(user_id,book_id))
    connec.commit()
    connec.close()
    return redirect(url_for('user_books',user_id=user_id))

@app.route('/returnbook/<int:request_id>', methods=['GET','POST'])
def returnbook(request_id):
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    user_id=cursor.execute("SELECT user_id FROM BookRequests WHERE id=?",(request_id,)).fetchone()[0]
    book_id=cursor.execute("SELECT book_id FROM BookRequests WHERE id=?",(request_id,)).fetchone()[0]
    cursor.execute("DELETE FROM User_Books WHERE (UserID=? AND BookID=?)",(user_id,book_id))
    cursor.execute("UPDATE BookRequests SET status='returned' WHERE (user_id=? AND book_id=?)",(user_id,book_id))
    connec.commit()
    connec.close()
    return redirect(url_for('user_books',user_id=user_id))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    print(session)
    message= 'You have been logged out successfully.'
    flash(message,"info")
    return redirect(url_for('index'))

@app.route('/feedback/user<int:user_id>/book<int:book_id>', methods=['GET','POST'])
def feedback(user_id,book_id):
    connec =sqlite3.connect('librarydata.db')
    cursor = connec.cursor()
    if request.method=='POST':
        connec =sqlite3.connect('librarydata.db')
        cursor = connec.cursor()
        FeedbackText=request.form['feedbacktext']
        Rating=request.form['rating']
        if Rating=='' :
            message="Please fill all the required fields (*)"
            flash(message,"info")
            # return render_template("error.html",message=message)
            return redirect(url_for('feedback'))
        cursor.execute("INSERT INTO Feedback (UserID,BookID,FeedbackText,Rating) VALUES (?,?,?,?)", (user_id, book_id, FeedbackText,Rating))
        connec.commit()
        return redirect(url_for('user_books',user_id=user_id))
    bookname=cursor.execute("SELECT name FROM Books WHERE BookID=?",(book_id,)).fetchone()[0]
    connec.close()
    return render_template('feedbackform.html',bookname=bookname)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)