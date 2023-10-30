from db import db


class KeyTermGenModel(db.Model):
    __tablename__ = "keyterms_generated"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    keyterms = db.Column(db.String(2000), nullable=True)

    def json(self):
        return {
            "id": self.id,
            "text": self.text,
            "terms": self.keyterms.split('--|--'),
        }

    @classmethod
    def find_by_text(cls, text):
        return cls.query.filter_by(text=text).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class KeyTermSelectModel(db.Model):
    __tablename__ = "keyterms_selected"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    keyterms = db.Column(db.String(2000), nullable=True)

    def json(self):
        return {
            "id": self.id,
            "text": self.text,
            "terms": self.keyterms.split('--|--'),
        }

    @classmethod
    def find_by_text(cls, text):
        return cls.query.filter_by(text=text).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()