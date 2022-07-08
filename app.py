
from email.policy import EmailPolicy
from enum import unique
from flask import Flask, render_template, request, redirect, flash, session, url_for

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.sql'
app.config ["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "fs67ho3*Srb8bv-3r)=+ak"


db = SQLAlchemy(app)


class Userdb(db.Model):
    No = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(25), nullable=False)
    Password = db.Column(db.String(128), nullable=False)
    Username = db.Column(db.String(20), nullable = False, unique=True)
  
    User_notes = db.relationship("Notesdb", backref="userdb")
    
    def __init__(self, Email, Password, Username):
        self.Email = Email
        self.Password = Password
        self.Username = Username

class Notesdb(db.Model):
    No = db.Column(db.Integer, primary_key=True)
    Titles = db.Column(db.Text(120), nullable=True)
    Notes = db.Column(db.Text, nullable=True)
    #foreign key to link userid with notes(thid userid refers to primary key "No" of userdb table)
    User_id = db.Column(db.Integer, db.ForeignKey("userdb.No"), nullable=False)

    def __init__(self, Titles, Notes, User_id):
        self.Titles = Titles
        self.Notes = Notes
        self.User_id = User_id

    #def __init__(self,Titles, Notes):
        #self.Titles = Titles
        #self.Notes = Notes
    

    
   
@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/register/", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")
        #session["username"]= username
        #session["password"]= password
        email_match_obj = Userdb.query.filter_by(Email=email).first()
        username_match_obj = Userdb.query.filter_by(Username=username).first()
        
        if email == "" or password== "" or username == "":
            return render_template("register.html")
        else:
            
            if email_match_obj or username_match_obj is not None:
                
                if email_match_obj is not None:
                    flash("Email is alredy exist!", "info")
                    return redirect("/login/")
                    
                
                else:
                    flash("Username is alredy exist!", "info")
                    return redirect("/register/")
                    
            else:
                session["email"]= email
                acc_data = Userdb(email, password, username)
                db.session.add(acc_data)
                db.session.commit()
                flash("Signed Up Successfully.", "success")
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
            flash('New User! Create Your Account First.', 'info')
            return redirect ("/register/")
        else:
            password = request.form.get("password")
            found_user = Userdb.query.filter_by(Email=email, Password=password).first()
            if found_user is not None:
                if email not in session:
                    session["email"] = email
                    flash("Successfully logged in.", "success")
                    return redirect('/notes/')
                else:
                    flash("Successfully logged in.", "success")
                    return redirect('/notes/')
            else:
                flash("Error! Please, Check your password", "danger")
                return redirect("/login/")
            
    else:

        
        if session.get("email") is not None:
            flash("Session is restored!", "success")
            return redirect("/notes/")
        else:
            return render_template("login.html")

@app.route("/logout/")
def logout():
    session.pop("email", None)
    flash("You have been logged out!")
    return redirect("/login/")

@app.route("/notes/", methods=["GET", "POST"])
def add_notes():
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
                        full_note = Notesdb(title, note, user_no)
                        db.session.add(full_note)
                        db.session.commit()
                        flash("Your Note is being saved.","success")
                
                        return redirect("/notes/")
                    else:
                        return "Issue with the database"
                else:
                    return "There is an error with session"
        except Exception as e:
            return e
        
    else:
        note = request.form.get("Note")
        title = request.form.get("Title")
        if session.get("email") is not None:

            email = session["email"]
            if email is not None:

                user_data = Userdb.query.filter_by(Email=email).first()
                user_no = user_data.No
                
                note_list = Notesdb.query.filter_by(User_id=user_no).all()
                note_count = Notesdb.query.filter_by(User_id=user_no).count()

                if note is not None:
                    return render_template("notes.html", notes=note, note_list=note_list, note_count=note_count, username=email)
                else:
                    return render_template("notes.html", note_list=note_list, note_count=note_count, username=email)
            else:
                return redirect("/login/")
        else:
            flash("Session has expired! Please Sign Up or Login.", "warning")
            return redirect("/login/")
        #passing the note param to html page, without it we can not show the notes or text.

@app.route("/notes/delete/<int:note_no>", methods=["POST", "GET"])
def notedel(note_no):
    try:
        Notesdb.query.filter_by(No=note_no).delete()
        db.session.commit()
    #if found_note != None:
    #    Notesdb.query.filter_by(No=note_no).delete()
        return redirect("/notes/")
    except Exception as e:
        return "Something goes wrong, failed to delete your note"


@app.route("/notes/edit/<int:note_no>", methods=["POST", "GET"])
def note_edit(note_no):
    note_data_obj = Notesdb.query.filter_by(No=note_no).first()
   
    if request.method == "POST":
        title = request.form.get("Title")
        note = request.form.get("Note")
        
        note_data_obj.Titles = title
        note_data_obj.Notes = note
        db.session.commit()

        return redirect("/notes/")
    else:
        return render_template("edit.html", title=note_data_obj.Titles, note=note_data_obj.Notes)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
