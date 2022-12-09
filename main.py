# Author & Copyright @DebiprasadXD
from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import psycopg2
import bcrypt
from cryptography.fernet import Fernet
from datetime import datetime as dt
from flask_wtf.csrf import CSRFProtect
import os

import utils.validate_pass


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config('DB_URI')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = config('SECRET_KEY')
#app.config['WTF_CSRF_ENABLED'] = True
db = SQLAlchemy(app)

csrf = CSRFProtect(app)


class Userdb(db.Model):
    No = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(30), nullable=False)
    Password = db.Column(db.LargeBinary, nullable=False)
    Username = db.Column(db.String(20), nullable=False, unique=True)

    User_notes = db.relationship("Notesdb", backref="userdb")

    def __init__(self, Email, Password, Username):
        self.Email = Email
        self.Password = Password
        self.Username = Username


class Notesdb(db.Model):
    No = db.Column(db.Integer, primary_key=True)
    Titles = db.Column(db.LargeBinary, nullable=True)
    Notes = db.Column(db.LargeBinary, nullable=True)
    Date = db.Column(db.String, nullable=False)
    Key = db.Column(db.LargeBinary, unique=True)

    # foreign key to link userid with notes(thid userid refers to primary key "No" of userdb table)
    User_id = db.Column(db.Integer, db.ForeignKey("userdb.No"), nullable=False)

    def __init__(self, Titles, Notes, Date, Key, User_id):

        self.Titles = Titles
        self.Notes = Notes
        self.Date = Date
        self.Key = Key
        self.User_id = User_id


db.create_all()


@app.route("/")
def home():
    if session.get("email") is not None:
        return redirect("/notes/")

    return render_template("index.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        check_pass = utils.validate_pass.validate(password)

        if check_pass is not True:
            flash(check_pass, category="error")
            return redirect('/register/')
        else:
            email_match_obj = Userdb.query.filter_by(Email=email).first()
        username_match_obj = Userdb.query.filter_by(Username=username).first()

        if email == "" or password == "" or username == "":
            return render_template("register.html")
        else:

            if email_match_obj or username_match_obj is not None:

                if email_match_obj is not None:
                    flash("Email is alredy exist!", category="error")
                    return redirect("/login/")

                else:
                    flash("Username is alredy exist!", category="error")
                    return redirect("/register/")

            else:
                session["email"] = email
                # convert the password to byte-array(string)
                bytePwd = password.encode('utf-8')
                # generate salt for the password
                mySalt = bcrypt.gensalt()
                # generate hashed password with salt

                hashed_password = bcrypt.hashpw(bytePwd, mySalt)

                acc_data = Userdb(email, hashed_password, username)
                db.session.add(acc_data)
                # commit the values to db
                db.session.commit()
                flash("Sign Up Successful.", category="success")
                return redirect("/notes/")
    else:
        return render_template("register.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        #session_checkbox = request.form.get("session_checkbox")
        found_email = Userdb.query.filter_by(Email=email).first()
        if found_email is None:
            flash('New User! Create Your Account First.', category='error')
            return redirect("/register/")
        else:
            password = request.form.get("password")

            # convert the password to byte-array
            bytePwd = password.encode('utf-8')

            found_user = Userdb.query.filter_by(Email=email).first()
            if found_user is not None:

                # verify the password
                if bcrypt.checkpw(bytePwd, found_user.Password):
                    if email not in session:
                        session["email"] = email
                        flash("Successfully logged in!", category="success")
                        return redirect('/notes/')
                    else:
                        flash("Successfully logged in!", category="success")
                        return redirect('/notes/')
                else:
                    flash("Error! Please, Check your password!", category="error")
                    return redirect("/login/")

    else:

        if session.get("email") is not None:
            flash("Session restored!", category="success")
            return redirect("/notes/")
        else:
            return render_template("login.html")


@app.route("/logout/")
def logout():
    session.pop("email", None)
    flash('You have been logged out!', category='error')
    return redirect("/login/")


@app.route("/notes/", methods=["GET", "POST"])
def notes_func():
    if request.method == "POST":
        title = request.form.get("Title")
        note = request.form.get("Note")
        #search_keyword = request.form.get("Search")
        #found_note = Notesdb.query.filter_by(Notes=search_keyword).first()
        try:
            if title == "" and note == "":
                return redirect("/notes/")
            else:

                if session.get("email") is not None:
                    email = session["email"]

                    user_data = Userdb.query.filter_by(Email=email).first()
                    user_no = user_data.No

                    if user_no is not None:
                        # fetch time in str
                        now = dt.now()
                        date = now.strftime("%d/%m/%y")
                        # generate a key for each note
                        key = Fernet.generate_key()
                        # assign the key to a variable
                        f = Fernet(key)
                        # encrypt title,note of note by encoding to bytes
                        enctitle = f.encrypt(title.encode())
                        encnote = f.encrypt(note.encode())

                        # pass the args to notesdb class
                        full_note = Notesdb(
                            enctitle, encnote, date, key, user_no)

                        db.session.add(full_note)
                        # save it to db
                        db.session.commit()
                        flash("Note saved.", category="success")

                        return redirect("/notes/")
                    else:
                        return "Issue with the database"
                else:
                    return "There is an error with session"
        except Exception as e:
            return e

    else:

        if session.get("email") is not None:

            email = session["email"]
            if email is not None:

                user_data = Userdb.query.filter_by(Email=email).first()
                user_no = user_data.No
                username = user_data.Username
                note_list = Notesdb.query.filter_by(
                    User_id=user_data.No).order_by(desc(Notesdb.No))
                # note_list = db.query(Notesdb.User_id).distinct(user_data.No) \ .order_by(Notesdb.Date)

                new_notelist = []
                for note_data in note_list:
                    note_no = note_data.No
                    # get the key from db
                    key = note_data.Key
                    # assign the key to a variable
                    f = Fernet(key)
                    # decrypt the title, note
                    dectitle = f.decrypt(note_data.Titles).decode()
                    decnote = f.decrypt(note_data.Notes).decode()
                    # append it to list as dic ,so it can be easily retrived by html page
                    notes_dic = {'No': note_no, 'Title': dectitle,
                                 'Note': decnote, 'Date': note_data.Date}
                    new_notelist.append(notes_dic)

                note_count = Notesdb.query.filter_by(User_id=user_no).count()
                return render_template("notes.html", note_list=new_notelist, note_count=note_count, username=username, email=email)
            else:
                return redirect("/login/")
        else:
            flash("Session has expired! Please Sign Up or Login.", category="error")
            return redirect("/login/")
        # passing the note param to html page, without it we can not show the notes or text.


@app.route("/notes/detail/<int:note_no>/", methods=["POST", "GET"])
def note_detail(note_no):
    note_data_obj = Notesdb.query.filter_by(No=note_no).first()
    email = session["email"]
    user_data_obj = Userdb.query.filter_by(Email=email).first()
    f = Fernet(note_data_obj.Key)
    key = Fernet(note_data_obj.Key)
    dectitle = key.decrypt(note_data_obj.Titles).decode()
    decnote = key.decrypt(note_data_obj.Notes).decode()
    return render_template('note_detail.html', title=dectitle, note=decnote, note_no=note_no)


@app.route("/notes/search_results/", methods=['POST', 'GET'])
def search_note():
    if request.method == "GET":
        search = request.args.get('search')
        if search == '':
            flash('Empty query', category='error')
            return redirect('/notes/')

        #notes_list = Notesdb.query.filter(Notesdb.Notes.like('%' + search + '%'))
        #notes_list = notes_list.order_by(Notesdb.Titles).all()
        else:
            if session.get("email") is not None:

                email = session["email"]
                if email is not None:
                    user_data = Userdb.query.filter_by(Email=email).first()
                    notes_list = Notesdb.query.filter_by(
                        User_id=user_data.No).all()

                    new_notelist = []
                    for note_data in notes_list:
                        note_no = note_data.No
                        # get the key from db
                        key = note_data.Key
                        # assign the key to a variable
                        f = Fernet(key)
                        # decrypt the title, note
                        dectitle = f.decrypt(note_data.Titles).decode()
                        decnote = f.decrypt(note_data.Notes).decode()

                        # combine note and title for search_text
                        search_text = decnote.lower() + ' ' + dectitle.lower()
                        search_term = search.lower()
                        # find if there any maching words available
                        if search_text.find(search_term) == -1:
                            pass

                        else:
                            # append it to list as dic ,so it can be easily retrived by html page
                            notes_dic = {'No': note_no, 'Title': dectitle,
                                         'Note': decnote, 'Date': note_data.Date}
                            new_notelist.append(notes_dic)

                    if len(new_notelist) == 0:
                        flash('No results found', category='error')
                        return redirect('/notes/')
                    else:
                        return render_template('search_result.html', note_list=new_notelist, note_count=len(new_notelist))


@app.route("/notes/delete/<int:note_no>/", methods=["POST", "GET"])
def notedel(note_no):
    try:
        Notesdb.query.filter_by(No=note_no).delete()
        db.session.commit()

        flash("Note Deleted", category="error")
        return redirect("/notes/")
    except Exception as e:
        flash("Something goes wrong, failed to delete your note", category="error")
        return ("/notes/")


@app.route("/notes/edit/<int:note_no>/", methods=["POST", "GET"])
def note_edit(note_no):
    note_data_obj = Notesdb.query.filter_by(No=note_no).first()
    email = session["email"]
    user_data_obj = Userdb.query.filter_by(Email=email).first()

    f = Fernet(note_data_obj.Key)

    if request.method == "POST":
        title = request.form.get("Title")
        note = request.form.get("Note")

        note_data_obj.Titles = f.encrypt(title.encode())
        note_data_obj.Notes = f.encrypt(note.encode())

        db.session.commit()

        flash("Note Edited", category="success")
        return redirect("/notes/")
    else:
        key = Fernet(note_data_obj.Key)
        dectitle = key.decrypt(note_data_obj.Titles).decode()
        decnote = key.decrypt(note_data_obj.Notes).decode()

        return render_template("edit.html", title=dectitle, note=decnote)


@app.route("/about/")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    db.create_all()
    app.run(port=os.getenv("PORT", default=8000))
