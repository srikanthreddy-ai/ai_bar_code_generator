class Book:
    def __init__(self, id, title, author):
        self.id = id
        self.title = title
        self.author = author

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
        }
