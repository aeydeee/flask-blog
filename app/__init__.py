# app/__init__.py
import os
import uuid

from flask import Flask, render_template, flash, request, url_for, redirect
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from app.webforms import PasswordForm, UserForm, NamerForm, PostForm, LoginForm, SearchForm
from flask_ckeditor import CKEditor

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # Add ckeditor
    ckeditor = CKEditor(app)
    # Old SQLite DB
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    # New MySQL DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/users'
    # Secret key!
    app.config['SECRET_KEY'] = "my super secret key that needs to secure"

    UPLOAD_FOLDER = 'static/images/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)
    migrate = Migrate(app, db)

    # Import models here to avoid circular import issues

    from .models import Users, Posts

    from app.webforms import PasswordForm, UserForm, NamerForm, PostForm

    # Flask_Login Stuff
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    @app.route("/admin")
    @login_required
    def admin():
        id = current_user.id
        if id == 11:
            return render_template("admin.html")
        else:
            flash("Sorry you must be the Admin to Access the Admin Page....")
            return redirect(url_for('dashboard'))

    @app.route("/")
    def index():
        first_name = "John"
        stuff = 'This is bold text'
        favorite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
        return render_template("index.html",
                               first_name=first_name,
                               stuff=stuff,
                               favorite_pizza=favorite_pizza)

    # Json Thing
    @app.route('/date')
    def get_current_date():
        favorite_pizza = {
            'John': 'Pepperoni',
            'Mary': 'Cheese',
            'Bob': 'Mushroom',
            'Tim': 'Hawaiian'
        }
        # return {'Date': date.today()}
        return favorite_pizza

    # Create a route decorator
    @app.route("/user/add", methods=["GET", "POST"])
    def add_user():
        name = None
        form = UserForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                # hash password!!
                hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2")
                user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                             favorite_color=form.favorite_color.data,
                             password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash = ''

            flash('User Added Successfully')
        our_users = Users.query.order_by(Users.date_created).all()
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)

    @app.route("/user/<name>")
    def user(name):
        return render_template("user.html", name=name)

    # Update Database Record
    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    @login_required
    def update(id):
        form = UserForm()
        name_to_update = Users.query.get_or_404(id)
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            name_to_update.favorite_color = request.form['favorite_color']
            name_to_update.username = request.form['username']
            try:
                db.session.commit()
                flash('User Updated Successfully', 'success')
                return render_template("update.html",
                                       form=form,
                                       name_to_update=name_to_update)
            except:
                flash('Error! Looks like there was a problem... try again', 'error')
                return render_template("update.html",
                                       form=form,
                                       name_to_update=name_to_update)
        else:
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)

    # Create a Password Test Page
    @app.route('/test_pw', methods=['GET', 'POST'])
    def test_pw():
        email = None
        password = None
        pw_to_chk = None
        passed = None
        form = PasswordForm()

        # Validate Form
        if form.validate_on_submit():
            email = form.email.data
            password = form.password_hash.data
            # Clear the Form fields
            form.email.data = ''
            form.password_hash.data = ''

            # Lookup user by email address
            pw_to_chk = Users.query.filter_by(email=email).first()
            if pw_to_chk:
                # Check Hash ed Password
                passed = check_password_hash(pw_to_chk.password_hash, password)
            else:
                flash('Email not found', 'error')

            # flash('Form Submission Success')
        return render_template("test_pw.html",
                               email=email,
                               password=password,
                               pw_to_chk=pw_to_chk,
                               passed=passed,
                               form=form)

    # Create Name Page
    @app.route('/name', methods=['GET', 'POST'])
    def name():
        name = None
        form = NamerForm()
        if form.validate_on_submit():
            name = form.name.data
            form.name.data = ''
            flash('Form Submission Success')
        return render_template("name.html", name=name, form=form)

    # Delete a user
    @app.route('/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def delete(id):
        if id == current_user.id:
            user_to_delete = Users.query.get_or_404(id)
            name = None
            form = UserForm()
            try:
                db.session.delete(user_to_delete);
                db.session.commit()
                flash('User deleted successfully', 'success')
                our_users = Users.query.order_by(Users.date_created).all()
                return render_template("add_user.html",
                                       form=form,
                                       name=name,
                                       our_users=our_users)
            except:
                flash('Whoops! problem deleting the user')
                our_users = Users.query.order_by(Users.date_created).all()
                return render_template("add_user.html",
                                       form=form,
                                       name=name,
                                       our_users=our_users)
        else:
            flash('Sorry, You can\'t delete that user')
            return redirect(url_for('dashboard'))

    # Add Post Page
    @app.route('/add-post', methods=['POST', 'GET'])
    # @login_required
    def add_post():
        form = PostForm()

        if form.validate_on_submit():
            poster = current_user.id
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         poster_id=poster,
                         slug=form.slug.data)
            # Clear the Form
            form.title.data = ''
            form.content.data = ''
            # form.author.data = ''
            form.slug.data = ''

            # Add the post to database
            db.session.add(post)
            db.session.commit()

            flash('Blog post submitted successfully!', 'success')

        # Redirect to the webpage
        return render_template('add_post.html', form=form)

    @app.route('/posts')
    def posts():
        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

    @app.route('/posts/<int:id>')
    def post(id):
        post = Posts.query.get_or_404(id)
        return render_template('post.html', post=post)

    @app.route('/posts/edit/<int:id>', methods=['POST', 'GET'])
    @login_required
    def edit_post(id):
        form = PostForm()
        post = Posts.query.get_or_404(id)

        if form.validate_on_submit():
            post.title = form.title.data
            # post.author = form.author.data
            post.slug = form.slug.data
            post.content = form.content.data
            # Update Database
            db.session.add(post)
            db.session.commit()
            flash('Post Has Been Updated!')
            return redirect(url_for('post', id=post.id))

        if current_user.id == post.poster_id:
            form.title.data = post.title
            # form.author.data = post.author
            form.slug.data = post.slug
            form.content.data = post.content
            return render_template('edit_post.html', form=form)
        else:
            flash('You aren\'t Authorized to edit this post`')
            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)

    @app.route('/posts/delete/<int:id>')
    @login_required
    def delete_post(id):
        post_to_delete = Posts.query.get_or_404(id)
        id = current_user.id
        if id == post_to_delete.poster.id:

            try:
                db.session.delete(post_to_delete)
                db.session.commit()

                flash('Blog Post Was Deleted!')

                # Grab all the posts from the database
                posts = Posts.query.order_by(Posts.date_posted)
                return render_template('posts.html', posts=posts)

            except:
                flash('Woops! There was a problem deleting the post, try again')

                # Grab all the posts from the database
                posts = Posts.query.order_by(Posts.date_posted)
                return render_template('posts.html', posts=posts)
        else:
            flash('You aren\'t authorized to Delete that Post!')

            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)

    # Create a Login Page
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user:
                # Check the hash
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user)
                    flash('Successfully logged in!')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Woops! Wrong password - Try Again!', 'error')
            else:
                flash('That User Doesn\'t Exist', 'error')

        return render_template('login.html', form=form)

    # Create a Logout Page
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        flash('Successfully logged out')
        return redirect(url_for('login'))

    # Create a Dashboard Page
    @app.route('/dashboard', methods=['POST', 'GET'])
    @login_required
    def dashboard():
        form = UserForm()
        id = current_user.id
        name_to_update = Users.query.get_or_404(id)
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            name_to_update.favorite_color = request.form['favorite_color']
            name_to_update.username = request.form['username']
            name_to_update.about_author = request.form['about_author']
            name_to_update.profile_pic = request.files['profile_pic']

            # Grab image Name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)

            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename

            # Save That Image
            saver = request.files['profile_pic']

            # Change it to a string to save to the database
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User Updated Successfully', 'success')
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update)
            except:
                flash('Error! Looks like there was a problem... try again', 'error')
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update)
        else:
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        return render_template('dashboard.html')

    # Pass Stuff to Navbar
    @app.context_processor
    def base():
        form = SearchForm()
        return dict(form=form)

    # Create Search Function
    @app.route('/search', methods=['POST'])
    def search():
        form = SearchForm()
        posts = Posts.query
        if form.validate_on_submit():
            # Get data from submitted form
            search_term = form.searched.data
            # Query the Database
            posts = posts.filter(
                or_(Posts.content.like(f'%{search_term}%'), Posts.title.like(f'%{search_term}%'))
            )
            posts = posts.order_by(Posts.title).all()

            return render_template("search.html",
                                   form=form,
                                   searched=search_term,
                                   posts=posts)

    # Create a Custom Error Pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    # Ensure the database is created
    with app.app_context():
        db.create_all()

    return app
