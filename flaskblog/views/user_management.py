from flask import Blueprint
from flask import render_template, flash, request
from werkzeug.security import generate_password_hash
from flask_login import login_required
from webforms import UserForm, NamerForm
from models import db, Users

manage_users = Blueprint('user_management', __name__)

@manage_users.route('/name', methods=['GET', 'POST'])
@login_required
def name():
    name = None
    form = NamerForm()

    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successful")

    context = {
        'name': name,
        'form': form
    }
    return render_template('user_management/name.html', **context)

@manage_users.route('/profile/<name>')
@login_required
def profile(name):
    context = {
        'name': name
    }
    return render_template('user_management/profile.html', **context)

@manage_users.route('/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()

    # validate form
    if form.validate_on_submit():
        # check if database consist the same email
        username = form.username.data
        name = form.name.data
        email = form.email.data
        mobile = form.mobile.data
        password_hash = form.password_hash.data
        user = Users.query.filter_by(email=email).first()
        if user is None:
            # hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user = Users(username=username, name=name, email=email, mobile=mobile, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            message = "User Added Successfully"
        else:
            message = "Email Registered Before"
        
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.mobile.data = ''
        form.password_hash.data = ''
        flash(message)

    user_list = Users.query.order_by(Users.date_added)

    context = {
        'form': form,
        'user_list': user_list
    }
    return render_template('user_management/add_user.html', **context)

@manage_users.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()

    user_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.mobile = request.form['mobile']
        user_to_update.about_author = request.form['about_author']
        try:
            # save into database
            db.session.commit()
            flash("User Updated Successfully")
        except:
            flash("User Not Found")

    context = {
        'form': form,
        'user_to_update': user_to_update
    }
    return render_template('user_management/update_user.html', **context)

@manage_users.route('/delete/<int:id>')
@login_required
def delete_user(id):
    form = UserForm()

    user_to_delete = Users.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
    except:
        flash("User Not Found")

    user_list = Users.query.order_by(Users.date_added)

    context = {
        'form': form,
        'user_list': user_list
    }
    return render_template('user_management/add_user.html', **context)