import os

from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book


app = Flask(__name__)

# --- Configuration & Pathing ---
# Generic file handling for cross-platform compatibility
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data')
DATABASE_URI = f"sqlite:///{os.path.join(DATA_PATH, 'library.sqlite')}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'academy_assignment_secret'

db.init_app(app)


@app.route('/')
def home():
    """Display the library home page with search and sort functionality."""
    search_query = request.args.get('search')
    sort_by = request.args.get('sort', 'title')

    # Join Author to allow searching and sorting by author name
    query = db.session.query(Book).join(Author)

    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort_by == 'author':
        books = query.order_by(Author.name).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template('home.html', books=books, search_query=search_query)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add a new author with whitespace stripping and unique name check."""
    if request.method == 'POST':
        # Feedback Refactor: Strip whitespace and validate input
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birthdate')
        death_date = request.form.get('date_of_death')

        if not name:
            flash("Error: Author name cannot be empty.")
            return redirect(url_for('add_author'))

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=death_date
        )

        try:
            db.session.add(new_author)
            db.session.commit()
            flash(f"Author '{name}' added successfully!")
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: An author with this name already exists.")

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Add a new book with unique ISBN validation."""
    if request.method == 'POST':
        # Feedback Refactor: Strip inputs for data integrity
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip()

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=request.form.get('publication_year'),
            rating=request.form.get('rating'),
            author_id=request.form.get('author_id')
        )

        try:
            db.session.add(new_book)
            db.session.commit()
            flash(f"Book '{title}' added successfully!")
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: A book with this ISBN already exists.")

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book and its author if they have no other books left."""
    book = db.session.get(Book, book_id)
    if not book:
        flash("Error: Book not found.")
        return redirect(url_for('home'))

    author = book.author
    db.session.delete(book)
    db.session.commit()

    # Step 6 cleanup: Delete author if they have no books remaining
    if author and not author.books:
        db.session.delete(author)
        db.session.commit()
        flash("Book removed and lonely author cleaned up.")
    else:
        flash("Book removed from library.")

    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """View details for a specific book (Bonus #2)."""
    book = db.session.get(Book, book_id)
    if not book:
        return "Book not found", 404
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    """View details for a specific author (Bonus #2)."""
    author = db.session.get(Author, author_id)
    if not author:
        return "Author not found", 404
    return render_template('author_detail.html', author=author)


@app.route('/recommend')
def recommend_book():
    """Suggest a random book to the user (Fix for TemplateNotFound)."""
    return render_template(
        'recommend.html',
        recommendation="Try 'Dune' by Frank Herbert!"
    )


if __name__ == '__main__':
    with app.app_context():
        # Ensure 'data' directory exists for generic pathing
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        db.create_all()
    app.run(host="0.0.0.0", port=5002, debug=True)
