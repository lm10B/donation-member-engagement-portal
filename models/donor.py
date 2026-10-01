from extensions import db


class Donor(db.Model):

    __tablename__ = "donors"

    donor_id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    address = db.Column(
        db.String(255),
        nullable=True
    )