from flask import Blueprint
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from webforms import PostForm
from models import db, Posts

manage_posts = Blueprint('post_management', __name__)

@manage_posts.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)

    content = {
        'posts': posts
    }
    return render_template('post_management/posts.html', **content)

@manage_posts.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        user = current_user.id
        title = form.title.data
        content = form.content.data
        slug = form.slug.data
        post = Posts(user_id=user, title=title, content=content, slug=slug)

        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully")

    content = {
        'form': form
    }
    return render_template('post_management/add_post.html', **content)

@manage_posts.route('/post/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)

    content = {
        'post': post
    }
    return render_template('post_management/post.html', **content)

@manage_posts.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Updated Successfully")

        return redirect(url_for('post_management.post', id=post.id))
    
    if current_user.id == post.user_id:
        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug

        content = {
            'post': post,
            'form': form
        }
        return render_template('post_management/update_post.html', **content)
    else:
        flash("You can't update the post as you are not the author")
        return redirect(url_for('post_management.posts'))

@manage_posts.route('/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.user.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post Deleted Successfully")
        except:
            flash("Post Not Found")
    else:
        flash("You can't delete the post as you are not the author")

    return redirect(url_for('post_management.posts'))