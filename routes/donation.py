from flask import Blueprint, render_template, request

from extensions import db
from models.donor import Donor
from models.donation import Donation


donation_bp = Blueprint(
    "donation",
    __name__
)


@donation_bp.route(
    "/add-donation",
    methods=["GET", "POST"]
)
def add_donation():

    error_message = ""
    success_message = ""

    if request.method == "POST":

        # -----------------------------------------
        # GET DONOR INFORMATION
        # -----------------------------------------

        name = request.form.get(
            "name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        phone = request.form.get(
            "phone", ""
        ).strip()

        address = request.form.get(
            "address", ""
        ).strip()

        # -----------------------------------------
        # GET DONATION INFORMATION
        # -----------------------------------------

        amount = request.form.get(
            "amount", ""
        ).strip()

        payment_method = request.form.get(
            "payment_method", ""
        ).strip()

        transaction_id = request.form.get(
            "transaction_id", ""
        ).strip()

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not name:

            error_message = "Please enter your name."

        elif not email:

            error_message = "Please enter your email address."

        elif not amount:

            error_message = "Please enter a donation amount."

        elif not payment_method:

            error_message = "Please select a payment method."

        else:

            try:

                amount_value = float(amount)

                # ---------------------------------
                # CHECK AMOUNT
                # ---------------------------------

                if amount_value <= 0:

                    error_message = (
                        "Donation amount must be "
                        "greater than zero."
                    )

                else:

                    # ---------------------------------
                    # CHECK TRANSACTION ID
                    # ---------------------------------

                    if transaction_id:

                        existing_transaction = (
                            Donation.query.filter_by(
                                transaction_id=transaction_id
                            ).first()
                        )

                        if existing_transaction:

                            error_message = (
                                "This transaction ID "
                                "has already been used."
                            )

                            return render_template(
                                "add_donation.html",
                                error_message=error_message,
                                success_message=""
                            )

                    # ---------------------------------
                    # FIND EXISTING DONOR
                    # ---------------------------------

                    donor = Donor.query.filter_by(
                        email=email
                    ).first()

                    # ---------------------------------
                    # CREATE NEW DONOR
                    # ---------------------------------

                    if donor is None:

                        donor = Donor(
                            name=name,
                            email=email,
                            phone=phone,
                            address=address
                        )

                        db.session.add(donor)

                        # Generate donor_id
                        db.session.flush()

                    # ---------------------------------
                    # UPDATE EXISTING DONOR
                    # ---------------------------------

                    else:

                        donor.name = name
                        donor.phone = phone
                        donor.address = address

                    # ---------------------------------
                    # CREATE DONATION
                    # ---------------------------------

                    donation = Donation(
                        donor_id=donor.donor_id,
                        amount=amount_value,
                        payment_method=payment_method,
                        payment_status="Completed",
                        transaction_id=(
                            transaction_id
                            if transaction_id
                            else None
                        )
                    )

                    # ---------------------------------
                    # SAVE DATABASE
                    # ---------------------------------

                    db.session.add(donation)

                    db.session.commit()

                    # ---------------------------------
                    # SUCCESS MESSAGE
                    # ---------------------------------

                    success_message = (
                        f"Donation saved successfully. "
                        f"Thank you, {donor.name}! "
                        f"Your donation of "
                        f"${amount_value:.2f} "
                        f"has been recorded."
                    )

                    # Clear form after successful save
                    return render_template(
                        "add_donation.html",
                        success_message=success_message,
                        error_message=""
                    )

            except ValueError:

                error_message = (
                    "Please enter a valid donation amount."
                )

            except Exception as error:

                db.session.rollback()

                print(
                    "Donation Error:",
                    error
                )

                error_message = (
                    "Unable to save donation. "
                    "Please try again."
                )

    # -----------------------------------------
    # DISPLAY PAGE
    # -----------------------------------------

    return render_template(
        "add_donation.html",
        error_message=error_message,
        success_message=success_message
    )