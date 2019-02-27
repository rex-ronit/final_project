import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import os

from helpers import apology, login_required, lookup, usd
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['UPLOAD_FOLDER'] = "static/images"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        rows = db.execute("Select * from books")
        return render_template("index.html", rows = rows)
    else:
        search = request.form.get("search").title()
        k = len(search)
        tmp = []
        for i in range(k):
            tmp.append("%")
            tmp.append(search[i])
        tmp.append("%")
        mac = "".join(tmp)

        crit = request.form.get("sby")

        if not crit :
            rows = db.execute("Select * from books")
            return render_template("index.html", rows = rows)

        if crit == "n":
            rows = db.execute("Select * from books where bookname like :ser", ser = mac)

        if crit == "a":
            rows = db.execute("Select * from books where author like :ser", ser = mac)

        if crit == "c":
            rows = db.execute("Select * from books where class like :ser", ser = mac)

        if crit == "t":
            rows = db.execute("Select * from books where type like :ser", ser = mac)

        if crit == "s":
            rows = db.execute("Select * from books where subject like :ser", ser = mac)

        return render_template("index.html", rows = rows)


@app.route("/about_us")
@login_required
def about_us():
    return render_template("about_us.html")

@app.route("/share", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":

        return render_template("share.html", er = "Hello, World!")

    elif request.method == "POST":

        # get all the values from form

        target = os.path.join(APP_ROOT, 'static/images/')

        if not os.path.isdir(target):
            os.mkdir(target)

        mobile = request.form.get("mobile")
        email = request.form.get("email")
        city = request.form.get("city").title()
        state = request.form.get("state").title()
        book = request.form.get("book").title()
        author = request.form.get("author").title()
        typee = request.form.get("type")
        subject = request.form.get("subject")
        clas = request.form.get("class")
        cost = request.form.get("cost")
        #pic = request.files("file")

        tmp = [mobile, email, city, state, book, author, typee, subject, clas, cost]

        for k in tmp:
            if not k:
                 return render_template("share.html", er = str(k) + "Please fill all the required data")

        # if 'file' not in request.files:
        #     flash('No file part')
        #     return render_template("share.html", er = "No file!")
        file = request.files["pic"]

        if file.filename == '':
            flash('No selected file')
            return render_template("share.html", er = "No file selcted!")
        if file:
            filename = secure_filename(book + "_" + file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        # for file in request.files.getlist("photo"):
        #     filename = book + "_" + file.filename
        #     destination = "/".join([target, filename])
        # file.save(destination)

        img_name = filename

        # insert values in database

        db.execute("Insert into books(user_id, mobile, email, city, state, bookname, author, type, subject, class, cost, img_name) values(:i_d, :mob, :e, :city, :state, :bname, :author, :typee, :sub, :clas, :cost, :img)",
        i_d = session["user_id"], mob = mobile, e = email, city = city, state = state, bname = book, author = author, typee = typee, sub = subject, clas = clas, cost = cost, img = img_name)

        return redirect("/")

@app.route("/remove", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        rows = db.execute("Select * from books where user_id = :i_d", i_d = session["user_id"])

        return render_template("remove.html", rows = rows)
    else:

        bname = request.form.get("book")
        db.execute("DELETE from books where bookname = :name", name = bname)
        return redirect("/")

@app.route("/<string:book_name>", methods=["GET", "POST"])
@login_required
def about(book_name):
    rows = db.execute("Select * from books where bookname = :book", book = book_name)

    return render_template("book.html", rows = rows)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":



        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Please provide a Username"
            return render_template("login.html", error = error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Please provide a Password"
            return render_template("login.html", error = error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username;",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")

        if not name or not password:
            error = "Please provide a Username and Password"
            return render_template("register.html", error = error)

        test = request.form.get("confirmation")
        if password != test:
            error = "Passwords did not match"
            return render_template("register.html", error = error)

        phash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        result = db.execute("Select * from users where username = :name;", name = name)

        if result != [] :
            error = "Username already taken"
            return render_template("register.html", error = error)

        db.execute("Insert into users(username,hash) values(:username,:hash);", username = request.form.get("username"), hash = phash)
        row = db.execute("Select user_id from users where username = :uname;", uname = name)
        session["user_id"] = row[0]["user_id"]

        #db.execute("Insert into portfolio(user_id) values(:i)", i = row[0])
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
