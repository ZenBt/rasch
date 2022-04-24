from flask import redirect, render_template, request, url_for
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_required, login_user

from app import app
from forms import LoginForm, PostForm, RubricForm
from models import Admin, Archive, Posts, Rubrics, db
from service import AddPost, SidebarInfo

ckeditor = CKEditor(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


@lm.user_loader
def load_user(id):
    return Admin.query.get(int(id))


@app.route('/', methods=['POST', 'GET'])
def index():
    sidebar = SidebarInfo()
    return render_template('index.html', sidebar=sidebar)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.pwd.data

        admin = Admin.query.filter(
            Admin.username == username, Admin.password == password).first()
        if admin:
            login_user(admin)
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/admin/rubric')
@login_required
def rubric():
    rubric_list = Rubrics.query.order_by(Rubrics.id).all()
    return render_template('rubric.html', rubrics=rubric_list, model=Rubrics)


@app.route('/admin/posts')
@login_required
def posts():
    posts_list = Posts.query.all()
    return render_template('posts.html', posts=posts_list, model=Posts)


@app.route('/admin/archive')
@login_required
def archive():
    archive_list = Archive.query.all()
    return render_template('archive.html', archive=archive_list, model=Archive)


@app.route('/admin/admin-list')
@login_required
def admin_list():
    admins = Admin.query.all()
    return render_template('admin_list.html', admins=admins, model=Admin)


@app.route('/admin/add-admin', methods=['POST', 'GET'])
@login_required
def add_admin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.pwd.data
        db.session.add(Admin(username=username, password=password))
        db.session.commit()
        return redirect(url_for('admin_list'))
    return render_template('add-admin.html', form=form)


@app.route('/admin/add-post', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm()
    form.rubric.choices = [(rubric.id, rubric.title)
                           for rubric in Rubrics.query.all()]
    if not form.rubric.choices:
        return redirect(url_for('add_rubric'))
    if form.validate_on_submit():
        AddPost(title=form.title.data,
                post_date=form.date.data,
                content=form.content.data,
                rubric=form.rubric.data)
    return render_template('add_post.html', form=form)


@app.route('/admin/add-rubric', methods=['POST', 'GET'])
@login_required
def add_rubric():
    form = RubricForm()
    if form.validate_on_submit():
        title = form.title.data
        rubric = Rubrics(title=title)
        db.session.add(rubric)
        db.session.commit()
        return redirect(url_for('rubric'))
    return render_template('add_rubric.html', form=form)


@app.route('/<slug>', methods=['POST', 'GET'])
def show_rubric(slug):
    rubric = Rubrics.query.filter(Rubrics.slug == slug).first()
    # добавить сюда список постов относящихся к рубрике
    sidebar = SidebarInfo()
    return render_template('post.html', sidebar=sidebar, rubric=rubric)


@app.route('/<year>')
def archive_year(year):
    pass


@app.route('/<slug>')
def post_info(slug):
    return 'Test'
