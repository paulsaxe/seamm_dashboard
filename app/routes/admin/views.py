"""
Admin views
"""

from flask import render_template, redirect, url_for, flash, Response

from .forms import (
    CreateUserForm,
)

from flask_jwt_extended import jwt_optional

from . import admin

from app import db, authorize
from app.models import Role, Group
from app.routes.api.users import _process_user_body


@admin.route("/admin/manage_users")
@jwt_optional
def manage_users():
    if not authorize.has_role("admin"):
        return render_template("401.html")
    return render_template("admin/manage_users.html")

@admin.route("/admin/create_user", methods=["GET", "POST"])
@jwt_optional
def create_user():

    if not authorize.has_role("admin"):
        return render_template("401.html")

    form = CreateUserForm()
    form.groups.choices = [(g.name, g.name) for g in Group.query.all()]
    form.roles.choices = [(r.name, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        processed_form = _process_user_body(form.data)

        if isinstance(processed_form, Response):
            flash(
                f"Creating the user failed because of problems with the input data. Please check the inputs and try again."
            )
            return redirect(url_for("admin.create_user"))

        else:
            db.session.add(processed_form)
            db.session.commit()
            flash(f"The user {form.data['username']} has been created")
            return render_template("admin/manage_users.html")

    return render_template("admin/create_user.html", form=form)