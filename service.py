from datetime import date

from sqlalchemy import desc

from models import Admin, Archive, Posts, Rubrics, db


def add_to_db(instance) -> None:
    db.session.add(instance)
    db.session.commit()


class AddPost():

    def __init__(self, title: str, post_date: date, content: str, rubric: int) -> None:
        self.title = title
        self.date = post_date
        self.content = content
        self.rubric = rubric
        self.post_add()

    def get_date_id(self) -> int:
        last = Archive.query.order_by(desc(Archive.id)).first()
        if last is None:
            self.archive_add(self.date)
            return 1
        post_date = Archive.query.filter(Archive.date == self.date).first()
        if post_date is None:
            self.archive_add(self.date)
            return last.id + 1
        return post_date.id

    def archive_add(self, date) -> None:
        archive = Archive(date=date)
        add_to_db(archive)

    def post_add(self):
        date_id = self.get_date_id()
        post = Posts(title=self.title, content=self.content,
                     date_id=date_id, rubric_id=self.rubric)
        add_to_db(post)


class ArchiveInfo():

    def __getitem__(self, key):
        posts = [Posts.query.filter(Posts.id == post_id).first()
                 for post_id in self.get_posts_id()]
        return posts[key]

    def get_last_posts(self):
        return db.session.query(Posts, Archive).join(
            Archive, Posts.date_id == Archive.id).order_by(
                desc(Archive.date)).limit(5).all()

    def get_posts_id(self):
        return [post_id[0].id for post_id in self.get_last_posts()]


class SidebarInfo():

    @property
    def rubrics(self):
        return Rubrics.query.all()

    @property
    def new_posts(self):
        arc = ArchiveInfo()
        return arc

    @property
    def archive(self):
        ''' Добавить словарь формата 01: Январь, 02: Ферваль..., доставать и date
        год доставать date.today().strftime('%Y')
        месяц date.today().strftime('%m')
        объект класса datetime.date из бд 
        for dt in Archive.query.all():
            dt.date.strftime("%m")'''


class PostList():
    
    def __init__(self, slug) -> None:
        self._slug = slug
    
    def get_rubric(self) -> Posts:
        return Rubrics.query.filter(Rubrics.slug==self._slug).first()
    
    def get_posts_by_rubric(self):
        return Posts.query.filter(Posts.rubric_id==self.get_rubric().id).all()
    
    @property
    def rubric(self):
        return self.get_rubric().title
    @property
    def posts(self):
        return self.get_posts_by_rubric()
    
