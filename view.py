from flask import redirect, render_template, request, url_for
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_required, login_user

from app import app
from forms import LoginForm, PostForm, RubricForm, MainPageForm
from models import Admin, Archive, Posts, Rubrics, db, Slug
from service import AddPost, SidebarInfo, PostList, MainArticle, PostsFromArchive

ckeditor = CKEditor(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


@lm.user_loader
def load_user(id: int) -> Admin:
    return Admin.query.get(id)


@app.route('/', methods=['POST', 'GET'])
def index():
    sidebar = SidebarInfo()
    main_article_id = MainArticle.MAIN_ARTICLE_ID
    main_article = Posts.query.filter_by(id=main_article_id).first()
    return render_template('index.html', sidebar=sidebar, post=main_article)


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


@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    form = MainPageForm()
    form.article.choices = [(post.id, post.title)
                           for post in Posts.query.all()]
    
    if form.validate_on_submit():
        MainArticle.MAIN_ARTICLE_ID = form.article.data
    return render_template('admin.html', form=form)


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
        return redirect(url_for('posts'))
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
    post_list=PostList(slug)
    sidebar = SidebarInfo()
    return render_template('post.html', sidebar=sidebar, post_list=post_list)


@app.route('/<int:year>')
def archive_year(year):
    sidebar = SidebarInfo()
    posts = PostsFromArchive(year=year).get_posts_by_year_and_month()
    return render_template('post_archive.html', sidebar=sidebar, posts=posts)

@app.route('/<int:year>/<int:month>')
def archive_month(year, month):
    sidebar = SidebarInfo()
    posts = PostsFromArchive(year=year, month=month).get_posts_by_year_and_month()
    return render_template('post_archive.html', sidebar=sidebar, posts=posts, month=month)


@app.route('/post/<slug>')
def post_info(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    sidebar = SidebarInfo()
    
    return render_template('post_info.html', sidebar=sidebar, post=post)


@app.route('/admin/p/edit/<int:p_id>', methods=['POST', 'GET'])
@login_required
def edit_post(p_id: int):
    form = PostForm()
    article_body = Posts.query.filter_by(id=p_id).first()
    form.rubric.choices = [(rubric.id, rubric.title)
                           for rubric in Rubrics.query.all()]
    form.rubric.data = article_body.rubric_id
    form.content.data = article_body.content
    if not form.rubric.choices:
        return redirect(url_for('add_rubric'))
    if form.validate_on_submit():
        article_body.title=form.title.data
        article_body.content=form.content.data
        article_body.rubric_id=form.rubric.data
        article_body.date_id=AddPost.get_date_id(form.date.data)
        db.session.commit()
        return redirect(url_for('posts'))
    return render_template('edit_post.html', form=form, article_body=article_body)


@app.route('/admin/r/edit/<int:r_id>', methods=['POST', 'GET'])
@login_required
def edit_rubric(r_id: int):
    form = RubricForm()
    rubric = Rubrics.query.filter_by(id=r_id).first()

    if form.validate_on_submit():
        rubric.title = form.title.data
        rubric.slug = Slug(id=r_id, title=form.title.data).slug
        db.session.commit()
        return redirect(url_for('rubric'))
    return render_template('edit_rubric.html', form=form, rubric=rubric)


@app.route('/admin/del/<int:p_id>', methods=['POST', 'GET'])
@login_required
def del_item(p_id: int):
    model_dict = {'posts': Posts, 'admin': Admin, 'archive': Archive, 'rubric': Rubrics}
    model_key = request.args.get('model')
    model = model_dict[model_key]
    db.session.delete(model.query.filter_by(id=p_id).first())
    db.session.commit()
    return redirect(url_for(model_key))