import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, Bcrypt, mail
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

bcrypt = Bcrypt(app)


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts, title='Home')



@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('The email or password you have entered is incorrect! Please try again with correct credentials.', 'danger')
    return render_template('login.html', title='Log in', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    
    return picture_fn


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile',
                           image_file=image_file, form=form)

@app.route('/upload/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your video has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('upload.html', title='New Video', form=form, legend='Upload New Video')

@app.route('/video/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('video.html', title=post.title, post=post)


@app.route('/video/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your video info has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('upload.html', title='Update Video', form=form, legend='Edit Video Info')

@app.route('/video/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_video(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your video has been deleted!', 'success')
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    post = Post.query.filter_by(user_id=user.id).all()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('creator.html', title=user.username, post=post, user=user, image_file=image_file)
