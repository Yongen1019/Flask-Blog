from flask import Blueprint
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from webforms import PostForm
from models import db, Posts

admins = Blueprint('admin', __name__)

@admins.route('/')
@login_required
def admin():
    id = current_user.id
    if id == 11:
        return render_template('admin/admin.html')
    else:
        flash("Sorry, only admin can access the page")
        return redirect(url_for('dashboard'))