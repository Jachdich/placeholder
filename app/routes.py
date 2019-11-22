from flask import render_template, url_for, flash, redirect, request
from app import app, db, Bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

bcrypt = Bcrypt(app)

posts = [
    {
        'channel': 'Ashmit',
        'title': 'Video Post 1',
        'content': 'First post content',
        'upload_date': 'November 20, 2019'
    },
    {
        'channel': 'Jach',
        'title': 'Video Post 2',
        'content': 'Second post content',
        'upload_date': 'November 21, 2019'
    }
]


@app.route('/')
@app.route('/home')
def home():
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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')
