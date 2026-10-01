from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request
)

from sqlalchemy import func
from werkzeug.security import generate_password_hash

from extensions import db
from models.user import User
from models.donor import Donor
from models.donation import Donation


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================================
# ADMIN PROTECTION
# =========================================================

def admin_required(function):

    @wraps(function)
    def protected_function(*args, **kwargs):

        # User is not logged in
        if "user_id" not in session:

            return redirect(
                url_for("auth.login")
            )

        # User is logged in but is not admin
        if session.get("role", "").lower() != "admin":

            return redirect(
                url_for("main.home")
            )

        # User is admin
        return function(*args, **kwargs)

    return protected_function


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard")
@admin_required
def dashboard():

    # Total number of donations
    total_donations = Donation.query.count()

    # Total number of donors
    total_donors = Donor.query.count()

    # Total amount donated
    total_amount = db.session.query(
        func.sum(Donation.amount)
    ).scalar()

    # If there are no donations
    if total_amount is None:
        total_amount = 0

    return render_template(
        "dashboard.html",

        user_name=session.get("user_name"),
        role=session.get("role"),

        total_donations=total_donations,
        total_donors=total_donors,
        total_amount=total_amount
    )


# =========================================================
# VIEW DONATION RECORDS
# =========================================================

@admin_bp.route("/donations")
@admin_required
def donations():

    # Get all donation records
    # Newest donations appear first
    donation_records = (
        Donation.query
        .order_by(
            Donation.donation_date.desc()
        )
        .all()
    )

    # Statistics
    total_donations = Donation.query.count()

    total_donors = Donor.query.count()

    total_amount = db.session.query(
        func.sum(Donation.amount)
    ).scalar()

    if total_amount is None:
        total_amount = 0

    return render_template(
        "donations.html",

        donations=donation_records,

        total_donations=total_donations,
        total_donors=total_donors,
        total_amount=total_amount
    )


# =========================================================
# ADD ADMINISTRATOR
# =========================================================
#
# NOTE:
# This page is intentionally NOT protected for the
# current local Capstone prototype.
#
# URL:
# http://127.0.0.1:5000/add-user
#
# =========================================================

@admin_bp.route(
    "/add-user",
    methods=["GET", "POST"]
)
def add_user():

    error_message = ""
    success_message = ""

    # -----------------------------------------------------
    # WHEN FORM IS SUBMITTED
    # -----------------------------------------------------

    if request.method == "POST":

        # Get name
        name = request.form.get(
            "name", ""
        ).strip()

        # Get email
        email = request.form.get(
            "email", ""
        ).strip().lower()

        # Get password
        password = request.form.get(
            "password", ""
        )

        # Get confirm password
        confirm_password = request.form.get(
            "confirm_password", ""
        )


        # =================================================
        # VALIDATION
        # =================================================

        if not name:

            error_message = (
                "Please enter the administrator name."
            )


        elif not email:

            error_message = (
                "Please enter an email address."
            )


        elif not password:

            error_message = (
                "Please enter a password."
            )


        elif len(password) < 6:

            error_message = (
                "Password must be at least "
                "6 characters."
            )


        elif password != confirm_password:

            error_message = (
                "Passwords do not match."
            )


        else:

            # =================================================
            # CHECK EXISTING EMAIL
            # =================================================

            existing_user = User.query.filter_by(
                email=email
            ).first()


            if existing_user:

                error_message = (
                    "A user with this email "
                    "already exists."
                )


            else:

                try:

                    # =========================================
                    # CREATE ADMINISTRATOR
                    # =========================================

                    new_admin = User(

                        name=name,

                        email=email,

                        password_hash=(
                            generate_password_hash(
                                password
                            )
                        ),

                        role="admin"
                    )


                    # =========================================
                    # ADD TO DATABASE
                    # =========================================

                    db.session.add(
                        new_admin
                    )


                    # =========================================
                    # SAVE
                    # =========================================

                    db.session.commit()


                    # =========================================
                    # SUCCESS
                    # =========================================

                    success_message = (
                        f"Administrator {name} "
                        f"has been created successfully. "
                        f"You can now log in using this account."
                    )


                except Exception as error:

                    # Undo unfinished database changes
                    db.session.rollback()

                    # Print actual error in terminal
                    print(
                        "Add Admin Error:",
                        error
                    )

                    error_message = (
                        "Unable to create administrator. "
                        "Please try again."
                    )


    # =====================================================
    # DISPLAY ADD USER PAGE
    # =====================================================

    return render_template(
        "add_user.html",

        error_message=error_message,
        success_message=success_message
    )