from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(50), nullable=False)
    date_of_death = db.Column(db.String(50), nullable=True)

    # Relationship to allow Step 6 logic (checking if an author has books left)
    books = db.relationship('Book', backref='author', lazy=True)

    def __str__(self):
        return f"Author(name={self.name})"


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True)  # Step 4 uniqueness
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer)  # Bonus #4
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __str__(self):
        return f"Book(title={self.title}, isbn={self.isbn})"