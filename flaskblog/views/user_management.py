from flask import Blueprint, current_app
from flask import render_template, flash, request, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from webforms import UserForm, NamerForm
from models import db, Users
# to ensure secure image filename
from werkzeug.utils import secure_filename
import uuid as uuid
import os
# read and write image using path
import cv2

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
        user_previous_pic = user_to_update.profile_pic
        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.mobile = request.form['mobile']
        user_to_update.about_author = request.form['about_author']
        if request.files['profile_pic']:
            profile_picture = request.files['profile_pic']
            pic_filename = secure_filename(profile_picture.filename)
            # set UUID to make image filename unique
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # else: 
        #     # use default image as user profile picture
        #     profile_picture = cv2.imread(os.path.join(current_app.config['UPLOAD_FOLDER'], 'user.png'))
        #     # set UUID to make image filename unique
        #     pic_name = str(uuid.uuid1()) + "_" + "user.png"
        # grab image filename
            user_to_update.profile_pic = pic_name
            try:
                # save into database
                db.session.commit()
                # remove previous image
                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'],user_previous_pic)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], user_previous_pic))
                # save the image
                # if request.files['profile_pic']:
                profile_picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
                # else:
                #     cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name), profile_picture)
                flash("User Updated Successfully")
            except:
                flash("User Not Found")
        
        else:
            try:
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
    if id == current_user.id:
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
    else:
        flash("You can't delete the user")
        return redirect(url_for('dashboard'))