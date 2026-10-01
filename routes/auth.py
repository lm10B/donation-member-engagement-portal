from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from extensions import db
from models.user import User
from models.member import Member


auth_bp = Blueprint(
    "auth",
    __name__
)


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:

        if session.get("role", "").lower() == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        return redirect(
            url_for("main.home")
        )

    message = ""

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            session["user_id"] = user.user_id
            session["user_name"] = user.name
            session["role"] = user.role

            # Admin
            if user.role.lower() == "admin":

                return redirect(
                    url_for("admin.dashboard")
                )

            # Member
            return redirect(
                url_for("main.home")
            )

        message = "Incorrect email or password."

    return render_template(
        "login.html",
        message=message
    )


# =========================================================
# MEMBER REGISTRATION
# =========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    error_message = ""
    success_message = ""

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        phone = request.form.get(
            "phone", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not name:

            error_message = "Please enter your name."

        elif not email:

            error_message = "Please enter your email."

        elif not password:

            error_message = "Please enter a password."

        elif len(password) < 6:

            error_message = (
                "Password must be at least 6 characters."
            )

        elif password != confirm_password:

            error_message = (
                "Passwords do not match."
            )

        else:

            # Check existing USER email
            existing_user = User.query.filter_by(
                email=email
            ).first()

            # Check existing MEMBER email
            existing_member = Member.query.filter_by(
                email=email
            ).first()

            if existing_user or existing_member:

                error_message = (
                    "An account with this email "
                    "already exists."
                )

            else:

                try:

                    # ---------------------------------
                    # CREATE USER LOGIN ACCOUNT
                    # ---------------------------------

                    new_user = User(
                        name=name,
                        email=email,
                        password_hash=generate_password_hash(
                            password
                        ),
                        role="member"
                    )

                    db.session.add(new_user)

                    # Generate user_id
                    db.session.flush()

                    # ---------------------------------
                    # CREATE MEMBER PROFILE
                    # ---------------------------------

                    new_member = Member(
                        user_id=new_user.user_id,
                        name=name,
                        email=email,
                        phone=phone if phone else None,
                        status="active"
                    )

                    db.session.add(new_member)

                    db.session.commit()

                    success_message = (
                        "Registration successful! "
                        "You can now log in using "
                        "your email and password."
                    )

                    # Show clean form after success
                    return render_template(
                        "register.html",
                        success_message=success_message,
                        error_message=""
                    )

                except Exception as error:

                    db.session.rollback()

                    print(
                        "Registration Error:",
                        error
                    )

                    error_message = (
                        "Unable to complete registration. "
                        "Please try again."
                    )

    return render_template(
        "register.html",
        error_message=error_message,
        success_message=success_message
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("main.home")
    )