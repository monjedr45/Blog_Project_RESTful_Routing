from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer,Text, String, DateTime, Float, text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
from flask import Flask, render_template, redirect, jsonify, request
from flask import session as flask_session
from flask_ckeditor import CKEditorField, CKEditor
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
engine = create_engine('sqlite:///posts.db')
session = Session(engine)
Base = declarative_base()

class BlogPost(Base):
    __tablename__ = 'blog_post'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(250), nullable=False)
    img_url = Column(String(250), nullable=False)


Base.metadata.create_all(engine)


ckeditor = CKEditor(app)

class PostForm(FlaskForm):
    title = StringField('Blog Post title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    blog_image = StringField('Blog Image Url', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-outline-secondary float-left mt-15'})

class PostFormEdit(FlaskForm):
    title_edit = StringField('Blog Post title', validators=[DataRequired()])
    subtitle_edit = StringField('Subtitle', validators=[DataRequired()])
    name_edit = StringField('Your Name', validators=[DataRequired()])
    blog_image_edit = StringField('Blog Image Url', validators=[DataRequired()])
    body_edit = CKEditorField('Body', validators=[DataRequired()])
    submit_edit = SubmitField('Confirm chages', render_kw={'class': 'btn btn-outline-secondary float-left mt-15'})
                                                                                                                                  
@app.route('/', methods=['GET', 'POST'])
def home():
    blog = session.query(BlogPost).all()
    all_data_list = []
    for item in blog:
        blog_data = {
            "id": item.id,
            "title": item.title,
            "subtitle":item.subtitle,
            "date":item.date,
            "body":item.body,
            "author":item.author,
            "img_url":item.img_url,
        }

        all_data_list.append(blog_data)
    return render_template("index.html", posts=all_data_list)


@app.route('/contact')
def contact():
    return render_template("contact.html")    

@app.route('/about')
def about():
    return render_template("about.html")   
 
@app.route('/post', methods=['GET', 'POST'])
def post():
    post_id__ = request.args.get('post_id')
    blog = session.query(BlogPost).filter_by(id=post_id__).first()

    blog_data = {
        "id": blog.id,
        "title":blog.title,
        "subtitle":blog.subtitle,
        "author":blog.author,
        "body":blog.body,
        "date":blog.date,
        "img_url":blog.img_url,
    }

    return render_template("post.html", blog_data = blog_data)    

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    title__ = form.title.data
    subtitle__ = form.subtitle.data
    name__ = form.name.data
    blog_image__ = form.blog_image.data
    body__ = form.body.data
    today_date = dt.datetime.now().strftime("%B %d, %Y")   
    if form.validate_on_submit():
        add_record = BlogPost(
            title=title__,
            date = today_date,
            body=body__,
            author=name__,
            img_url=blog_image__,
            subtitle=subtitle__,
        )
        try:
            session.add(add_record)
            session.commit()
            return redirect('/')
        except Exception as e:
            print(f"An error occurred while trying to add coffee {add_record}: {e}")
            session.rollback()
    return render_template('make-post.html', form=form)


@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    form = PostFormEdit()
    post_bi_id = session.query(BlogPost).filter_by(id=post_id).first()
    if form.validate_on_submit() and request.method == 'POST':
        post_bi_id = session.query(BlogPost).filter_by(id=post_id).first()
        print(post_id)
        if post_bi_id:
            post_bi_id.title = form.title_edit.data
            post_bi_id.subtitle = form.subtitle_edit.data
            post_bi_id.author = form.name_edit.data
            post_bi_id.img_url = form.blog_image_edit.data
            post_bi_id.body = form.body_edit.data
            try:
                session.commit()
                return redirect(f'/post?post_id={post_id}')
            except Exception as e:
                print('Error:', e)
                session.rollback()
        else:
            print('Post not found')
            return render_template('edit-post.html', form=form)

    if request.method == 'GET':
        data__ = {
            "title":post_bi_id.title,
            "subtitle":post_bi_id.subtitle,
            "author":post_bi_id.author,
            "img_url":post_bi_id.img_url,
            "body":post_bi_id.body,
            "date":post_bi_id.date,
        }
        if post_bi_id:
            form.title_edit.data = data__["title"]
            form.subtitle_edit.data = data__["subtitle"]
            form.name_edit.data = data__["author"]
            form.blog_image_edit.data = data__["img_url"]
            form.body_edit.data = data__["body"]
            return render_template('edit-post.html',form=form)
        else:
            return jsonify({'error': 'Post not found'}), 404


    
@app.route('/delete-post/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post_by_id = session.query(BlogPost).filter_by(id=post_id).first()
    if post_by_id:
        try:
            session.delete(post_by_id)
            session.commit()
            return redirect('/')
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"message": "Post not found"}



if __name__ == "__main__":
    app.run(debug=True)