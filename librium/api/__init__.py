from .core import API, BookAPI
from librium.database import Genre, Language, Publisher, Series, Author, Book, Format

author = API(Author)
genre = API(Genre)
language = API(Language)
publisher = API(Publisher)
series = API(Series)
book = BookAPI(Book)
format = API(Format)
