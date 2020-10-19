import flask_login
from flask import Flask, render_template, url_for, request, redirect, flash, current_app
from flask_principal import Principal, RoleNeed, Permission, identity_changed, Identity, AnonymousIdentity
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_BINDS'] = {
    'message': 'sqlite:///message.db',
    'news': 'sqlite:///news.db',
    'urgent': 'sqlite:///urgent.db'
}
db = SQLAlchemy(app)
manager = LoginManager(app)
principals = Principal(app)





class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    surname = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)





class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Message(db.Model):
    __bind_key__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.Text, nullable=False)
    Surname = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Message %r>' % self.Name


class News(db.Model):
    __bind_key__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<News %r>' % self.Name


class Urgent(db.Model):
    __bind_key__ = 'urgent'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Urgent %r>' % self.Name


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')



    if login  and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page)

        else:
            flash("Please login or password or surname erorr")
    else:
        flash("Please login and password ")
    return render_template('login.html')

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()

    return render_template('index.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    surname = request.form.get('surname')

    if request.method == "POST":
        if not (login or password or surname or password2):
            flash("Заполните всё")
        elif password != password2:
            flash("Пароли не равны")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login,surname=surname,password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')


    return render_template('register.html')


@app.route('/test')
def test():
    user = User.query.all()
    return render_template('test.html', user=user)

@app.route('/user/<int:id>/del')
def user_delete(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        db.session.delete
        return redirect("/")

    except:
        return "При удалении статьи произошла ошибка"


@app.route('/timetable')
def timetable():
    return render_template('timetable.html')


@app.route('/')
def index():
    news = News.query.order_by(News.date.desc()).all()
    return render_template('index.html', news=news)


@app.route('/news/<int:id>/del')
def news_delete(id):
    news = News.query.get_or_404(id)
    try:
        db.session.delete(news)
        db.session.commit()
        return redirect("/")

    except:
        return "При удалении статьи произошла ошибка"


@app.route('/news/<int:id>/update', methods=["POST", 'GET'])
def news_update(id):
    news = News.query.get(id)

    if request.method == "POST":
        news.title = request.form['title']
        news.intro = request.form['intro']
        news.text = request.form['text']

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "При добавлении статьи произошла ошибка"

    else:

        return render_template("news_update.html", news=news)


@app.route('/news/<int:id>')
def news_detail(id):
    news = News.query.get(id)
    return render_template('news_detail.html', news=news)


@app.route('/urgent_create', methods=["POST", 'GET'])
def urgent_create():
    if request.method == "POST":

        text = request.form['text']
        urgent = Urgent(text=text)

        db.session.add(urgent)
        db.session.commit()
        return redirect("/urgent_create")


    else:
        return render_template('urgent_create.html')


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def posts_detail(id):
    article = Article.query.get(id)
    return render_template('posts-detail.html', article=article)


@app.route('/posts/<int:id>/del')
def posts_delete(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect("/posts")

    except:
        return "При удалении статьи произошла ошибка"


@app.route('/message/<int:id>/del')
def message_delete(id):
    message = Message.query.get_or_404(id)
    try:
        db.session.delete(message)
        db.session.commit()
        return redirect("/message")

    except:
        return "При удалении сообщения произошла ошибка"


@app.route('/message/<int:id>/update', methods=["POST", 'GET'])
def message_update(id):
    message = Message.query.get(id)

    if request.method == "POST":
        message.Name = request.form['Name']
        message.Surname = request.form['Surname']
        message.text = request.form['text']

        try:
            db.session.commit()
            return redirect("/message")
        except:
            return "При добавлении статьи произошла ошибка"

    else:

        return render_template("message_update.html", message=message)


@app.route('/posts/<int:id>/update', methods=["POST", 'GET'])
def create_update(id):
    article = Article.query.get(id)

    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect("/posts")
        except:
            return "При обновлении статьи произошла ошибка"

    else:

        return render_template("post_update.html", article=article)


@app.route('/create-article', methods=["POST", 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect("/posts")
        except:
            return "При добавлении статьи произошла ошибка"

    else:
        return render_template("create-article.html")


@app.route('/create_news', methods=["POST", 'GET'])
def create_news():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        news = News(title=title, intro=intro, text=text)

        try:
            db.session.add(news)
            db.session.commit()
            return redirect("/")
        except:
            return "При добавлении статьи произошла ошибка"

    else:
        return render_template("create_news.html")


@app.route('/news_selection')
def news_selection():
    return render_template("news_selection.html")


@app.route('/message', methods=["POST", 'GET'])
@login_required
def message():
    if request.method == "POST":

        Name = flask_login.current_user.login
        Surname = flask_login.current_user.surname
        text = request.form['text']
        message = Message(Name=Name, Surname=Surname, text=text)

        try:
            db.session.add(message)
            db.session.commit()
            return redirect("/message")
        except:
            return "При добавлении статьи произошла ошибка"

    else:



        message = Message.query.order_by(Message.date.desc()).all()
        return render_template('message.html', message=message)

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


if __name__ == "__main__":
    app.run(debug=True)
