from flask import Flask, request, redirect, render_template, flash
#from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:malongar12@localhost:5432/Users_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'malongar123'

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#toolbar = DebugToolbarExtension(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)




class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    
    user = db.relationship("Userpost", backref="user")

    @property
    def full_name(self):
        """Return full name of user."""

        return f"{self.first_name} {self.last_name}"




class Userpost(db.Model):

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
class Tag(db.Model):
    __tablname__ = "tag"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable= False)
    posts = db.relationship('Userpost', secondary="posts_tags", backref="tags", )

    
    

class PostTag(db.Model):
    __tablename__ = "posts_tags"
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)












@app.route('/')
def root():
    #Show recent list of posts, most-recent first.

    posts = Userpost.query.order_by(Userpost.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# User route

@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():
   # create new user

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():
    # create new user

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()
    flash(f"User {new_user.full_name} added.")

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    # specific user info

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    # edit an existing user

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    # updating an existing user

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()
    flash(f"User {user.full_name} edited.")

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.full_name} deleted.")

    return redirect("/users")


##############################################################################
# Posts route


@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    # Show a form to create a new post for a specific user

    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    # creating a new post for a specific user

    user = User.query.get_or_404(user_id)
    new_post = Userpost(title=request.form['title'],
                    content=request.form['content'],
                    user=user)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    # Show a page with info on a specific post

    post = Userpost.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    # Show a form to edit an existing post

    post = Userpost.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    # update an existing post

    post = Userpost.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited.")

    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    # deleting an existing post

    post = Userpost.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")


@app.route("/tag")
def tag():
    tag = Tag.query.all()
    
    return render_template("tags/index.html", tag = tag)



@app.route('/tags/new')
def tags_new_form():
    # create a new tag

    posts = Userpost.query.all()
    return render_template('tags/new.html', posts=posts)




@app.route("/tags/new", methods=["POST"])
def tags_new():
    # create a new tag

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Userpost.query.filter(Userpost.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")




@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    # Show a page with info on a specific tag

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    # edit an existing tag

    tag = Tag.query.get_or_404(tag_id)
    posts = Userpost.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)





@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    # updating an existing tag

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Userpost.query.filter(Userpost.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    # deleting an existing tag

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")

