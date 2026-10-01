from extensions import db
from datetime import datetime


class Donation(db.Model):

    __tablename__ = "donations"

    donation_id = db.Column(
        db.Integer,
        primary_key=True
    )

    donor_id = db.Column(
        db.Integer,
        db.ForeignKey("donors.donor_id"),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.String(50),
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        nullable=False,
        default="Completed"
    )

    transaction_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    donation_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    donor = db.relationship(
        "Donor",
        backref="donations"
    )