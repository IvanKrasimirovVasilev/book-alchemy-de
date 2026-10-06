import os
from datetime import datetime

from flask import Flask, render_template, request
from data_models import db, Author, Book


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

db.init_app(app)


@app.route("/")
def home():
    books = db.session.execute(
        db.select(Book)
    ).scalars().all()

    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = None

    if request.method == "POST":
        name = request.form["name"]
        birth_date = request.form["birth_date"]
        date_of_death = request.form.get("date_of_death")

        # String -> Python date
        birth_date = datetime.strptime(
            birth_date,
            "%Y-%m-%d"
        ).date()

        # Date of death is optional
        if date_of_death:
            date_of_death = datetime.strptime(
                date_of_death, "%Y-%m-%d"
            ).date()
        else:
            date_of_death = None

        # Create an Author object
        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        db.session.add(new_author)
        db.session.commit()

        message = "Author added successfully!"

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    message = None

    authors = db.session.execute(
        db.select(Author)
    ).scalars().all()

    if request.method == "POST":
        isbn = request.form["isbn"]
        title = request.form["title"]
        publication_year = int(request.form["publication_year"])
        author_id = int(request.form["author_id"])

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        message = "Book added successfully!"

    return render_template(
        "add_book.html",
        authors=authors,
        message=message
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)