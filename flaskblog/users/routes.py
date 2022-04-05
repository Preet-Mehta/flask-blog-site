import os

from flask import Blueprint, redirect, url_for, flash, render_template, request, current_app, abort
from flask_login import current_user, login_user, logout_user, login_required

from flaskblog import bcrypt, db
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordForm, RequestResetForm
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.password = hashed_pass
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created. You can log in now!", "success")
        return redirect(url_for("main.home"))

    return render_template("register.html", title="Register Page", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page[1:])
            return redirect(url_for("main.home"))

        flash("Login unsuccessful, check email & password !", "danger")
    return render_template("login.html", title="Login Page", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.pro_pic.data:
            old_pic = current_user.img_file
            current_user.img_file = save_picture(form.pro_pic.data)
            if old_pic != "default.jpeg":
                os.remove(os.path.join(current_app.root_path, "static/profile_pics", old_pic))
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated !", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    img_file = url_for("static", filename="profile_pics/" + current_user.img_file)
    return render_template("account.html", title="Account Page", img_file=img_file, form=form)


@users.route('/user/delete/<int:user_id>', methods=["POST"])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete != current_user:
        abort(403)
    posts_to_delete = Post.query.filter_by(author=current_user)
    for post in posts_to_delete:
        db.session.delete(post)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("Your account and blogs have been deleted successfully !", "success")
    return redirect(url_for("users.logout"))


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("No user with such email exists, ")
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid token found.", "warning")
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pass
        db.session.commit()
        flash(f"Your password has been updated. You can log in now!", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
