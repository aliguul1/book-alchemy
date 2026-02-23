import os
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from data_models import db, Author, Book

app = Flask(__name__)

# --- Configuration & Pathing ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'academy_assignment_secret'

db.init_app(app)


# --- Routes ---

@app.route('/')
def home():
    search_query = request.args.get('search')
    sort_by = request.args.get('sort', 'title')

    # Step 4 & 5: Join required for displaying Author next to Book and searching
    query = db.session.query(Book).join(Author)

    if search_query:
        query = query.filter(Book.title.like(f"%{search_query}%"))

    if sort_by == 'author':
        books = query.order_by(Author.name).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template('home.html', books=books, search_query=search_query)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        new_author = Author(
            name=request.form.get('name'),
            birth_date=request.form.get('birthdate'),
            date_of_death=request.form.get('date_of_death')
        )
        db.session.add(new_author)
        db.session.commit()
        flash("Author added successfully!")
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        new_book = Book(
            title=request.form.get('title'),
            isbn=request.form.get('isbn'),
            publication_year=request.form.get('publication_year'),
            rating=request.form.get('rating'),
            author_id=request.form.get('author_id')
        )
        try:
            db.session.add(new_book)
            db.session.commit()
            flash(f"Book '{new_book.title}' added!")
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: This ISBN already exists.")

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    db.session.delete(book)
    db.session.commit()

    # Step 6 cleanup: Delete author if they have no books left
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    flash("Book removed from library.")
    return redirect(url_for('home'))


# Bonus #2: Detail Pages
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author_detail.html', author=author)


# Bonus #5: AI Recommendation
@app.route('/recommend')
def recommend_book():
    return render_template('recommend.html', recommendation="Try 'Dune' by Frank Herbert!")


if __name__ == '__main__':
    with app.app_context():
        # Step 3: Create tables
        if not os.path.exists(os.path.join(basedir, 'data')):
            os.makedirs(os.path.join(basedir, 'data'))
        db.create_all()
    app.run(debug=True)