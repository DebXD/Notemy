from flask import Flask, render_template, request, redirect

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/note.sql'
#app.config ["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


class Notesdb(db.Model):
    No = db.Column("No", db.Integer, primary_key=True)
    Titles = db.Column(db.Text, nullable=False)
    Notes = db.Column(db.Text, nullable=False)

    def __init__(self, Titles, Notes):
        self.Titles = Titles
        self.Notes = Notes
        

@app.route("/")
def hello_world():
    return render_template("index.html")
    
@app.route("/add_notes/", methods=["GET","POST"])
def add_notes():
    if request.method == "POST":
        titles = request.form.get("Title")
        notes = request.form.get("Note")
        #found_note = Notesdb.query.filter_by(Notes=notes).first()
        try:
            if titles == "" and notes == "" :
                return redirect("/add_notes/")
            else:
                full_note = Notesdb(titles, notes)
                db.session.add(full_note)

                db.session.commit()

                note_list = Notesdb.query.all()
                note_count = Notesdb.query.count()
                
                return render_template("add_notes.html", titles=titles, notes=notes, note_list=note_list, note_count=note_count)
        except Exception as e:
            return e
        
    else:
        notes = request.form.get("Note")
        titles = request.form.get("Title")

        note_list = Notesdb.query.all()
        note_count = Notesdb.query.count()

        if notes is not None:
            return render_template("add_notes.html", notes=notes, note_list=note_list, note_count=note_count)
        else:
            return render_template("add_notes.html", note_list=note_list, note_count=note_count)
            
        #passing the notes param to html page, without it we can not show the notes or text.

@app.route("/add_notes/delete/<int:note_no>", methods=["POST", "GET"])
def notedel(note_no):
    Notesdb.query.filter_by(No=note_no).delete()
    db.session.commit()
    #if found_note != None:
    #    Notesdb.query.filter_by(No=note_no).delete()
    return redirect("/add_notes/")

@app.route("/add_notes/edit/<int:note_no>", methods=["POST", "GET"])
def note_edit(note_no):
    if request.method == "POST":
        return f"You are trying to edit {note_no} note"






if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
