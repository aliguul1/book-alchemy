from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Model representing a book author."""

    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Feedback Fix: Name must be unique to avoid dropdown ambiguity
    name = db.Column(db.String(100), nullable=False, unique=True)

    birth_date = db.Column(db.String(50), nullable=False)
    date_of_death = db.Column(db.String(50), nullable=True)

    # Relationship to allow author cleanup logic
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        return f"Author(name={self.name})"


class Book(db.Model):
    """Model representing a book in the library."""

    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Feedback Fix: ISBN must be unique and required
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f"<Book {self.title}>"

    def __str__(self):
        return f"Book(title={self.title}, isbn={self.isbn})"
