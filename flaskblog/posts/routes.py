from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required, current_user

from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint("posts", __name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        new_created_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        flash("New post has been created successfully !", "success")
        db.session.add(new_created_post)
        db.session.commit()
        return redirect(url_for("main.home"))

    return render_template("create_post.html", title="New Post", legend="Create Post", form=form)


@posts.route("/post/<int:post_id>")
def post(post_id):
    current_post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=current_post.title, post=current_post)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    updated_post = Post.query.get_or_404(post_id)

    if updated_post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        updated_post.title = form.title.data
        updated_post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated successfully !", "success")
        return redirect(url_for("posts.post", post_id=updated_post.id))
    elif request.method == "GET":
        form.title.data = updated_post.title
        form.content.data = updated_post.content

    return render_template("create_post.html", title="Update Post", legend="Update Post", form=form)


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if post_to_delete.author != current_user:
        abort(403)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash("Your post has been deleted successfully !", "success")
    return redirect(url_for("main.home"))
