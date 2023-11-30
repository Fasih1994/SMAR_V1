from db import db


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(255), default=None)
    formatted_phone_number = db.Column(db.String(20))
    name = db.Column(db.String(255))
    rating = db.Column(db.Float)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    category = db.Column(db.String(255))
    city = db.Column(db.String(255))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        # Delete associated reviews
        for review in self.reviews:
            review.delete_from_db()

        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, place_id:str = None):
        return cls.query.filter_by(place_id=place_id).first()


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(255))
    rating = db.Column(db.Float)
    text = db.Column(db.Text)
    time = db.Column(db.Integer)
    translated = db.Column(db.Boolean)
    profile_photo_url = db.Column(db.String(255))
    relative_time_description = db.Column(db.String(50))
    author_url = db.Column(db.String(255))
    language = db.Column(db.String(10))
    original_language = db.Column(db.String(10))

    # Foreign key relationship
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    place = db.relationship('Place', backref=db.backref('reviews', lazy='dynamic'))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()