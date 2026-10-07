import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from data_models import db, Author, Book
from sqlalchemy import or_


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

db.init_app(app)


@app.route("/")
def home():
    sort = request.args.get("sort")
    search = request.args.get("search")

    statement = db.select(Book)

    if sort == "title":
        statement = statement.order_by(Book.title)

    if sort == 'author':
        statement = statement.join(Author).order_by(Author.name)

    if sort == "year":
        statement = statement.order_by(Book.publication_year)

    if sort == 'newest':
        statement = statement.where(Book.publication_year > 2000).order_by(Book.publication_year)

    if search:
        statement = statement.join(Author).where(
            or_(
                Book.title.ilike(f"%{search}%"),
                Author.name.ilike(f"%{search}%"))
            )

    books = db.session.execute(
        statement
    ).scalars().all()

    return render_template("home.html", books=books, sort=sort)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = None
    error = None

    if request.method == "POST":
        name = request.form["name"]
        birth_date = request.form["birth_date"]
        date_of_death = request.form.get("date_of_death")

        try:
            # String -> Python date
            birth_date = datetime.strptime(
                birth_date,
                "%Y-%m-%d"
            ).date()

            # Date of death is optional
            if date_of_death:
                date_of_death = datetime.strptime(
                    date_of_death,
                    "%Y-%m-%d"
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

        except ValueError:
            error = "Please enter a valid date."

    return render_template(
        "add_author.html",
        message=message,
        error=error
    )

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    message = None
    error = None

    authors = db.session.execute(
        db.select(Author)
    ).scalars().all()

    if request.method == "POST":
        isbn = request.form["isbn"]
        # TODO: Add ISBN format validation when client requirements are defined
        title = request.form["title"]
        publication_year = int(request.form["publication_year"])
        author_id = int(request.form["author_id"])

        current_year = datetime.now().year

        if publication_year < 1000 or publication_year > current_year:
            error = f"Publication year must be between 1000 and {current_year}."
        else:

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
        message=message,
        error=error
    )

@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.session.execute(
        db.select(Book).where(Book.id == book_id)
    ).scalar_one_or_none()
    if book:
        db.session.delete(book)
        db.session.commit()

    return redirect(url_for("home"))

@app.route("/book/<int:book_id>")
def get_book(book_id):
    book = db.session.execute(
        db.select(Book).where(Book.id == book_id)
    ).scalar_one_or_none()

    return render_template(
        "book_detail.html", book=book
    )

@app.route("/author/<int:author_id>")
def get_author(author_id):
    author = db.session.execute(
        db.select(Author).where(Author.id == author_id)
    ).scalar_one_or_none()

    return render_template(
        "author_detail.html", author=author
    )

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)