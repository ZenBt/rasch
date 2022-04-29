from datetime import date

from sqlalchemy import desc

from models import Admin, Archive, Posts, Rubrics, db


def add_to_db(instance) -> None:
    db.session.add(instance)
    db.session.commit()


class AddPost():
    '''recieve title, date, content and rubric_id
    create instance of models.Posts class and add it to database'''

    def __init__(self, title: str, post_date: date, content: str, rubric: int) -> None:
        self.title = title
        self.date = post_date
        self.content = content
        self.rubric = rubric
        self._post_add()

    def _get_date_id(self) -> int:
        '''
        if there is no dates in database or recieved date not in database
        then add self.date to DB
        returns id of recived date
        '''
        last = Archive.query.order_by(desc(Archive.id)).first()
        if last is None:
            self._archive_add(self.date)
            return 1
        post_date = Archive.query.filter(Archive.date == self.date).first()
        if post_date is None:
            self._archive_add(self.date)
            return last.id + 1
        return post_date.id

    def _archive_add(self, date) -> None:
        '''add to database recived date'''
        archive = Archive(date=date)
        add_to_db(archive)

    def _post_add(self):
        '''add post with correct date and rubric id to database'''
        date_id = self._get_date_id()
        post = Posts(title=self.title, content=self.content,
                     date_id=date_id, rubric_id=self.rubric)
        add_to_db(post)


class ArchiveInfo():
    '''class that works like iterator. 
    Items are last 5 posts from db ordered by date field

    simply pass the instance of it to the render_temlate function
    and use {% for el in instance %} construction'''

    def __getitem__(self, key):
        posts = [Posts.query.filter(Posts.id == post_id).first()
                 for post_id in self._get_posts_id()]
        return posts[key]

    def _get_last_posts(self) -> list:
        '''returns list of posts with joined dates ordered by dates'''
        return db.session.query(Posts, Archive).join(
            Archive, Posts.date_id == Archive.id).order_by(
                desc(Archive.date)).limit(5).all()

    def _get_posts_id(self) -> list:
        '''returns list of ids last posts'''
        return [post_id[0].id for post_id in self._get_last_posts()]


class SidebarInfo():
    '''three property functions contains all information
    that needs to be displayed at sidebar throughout all web-site

    simply pass the instance of it to the render_temlate function
    and call property methods'''

    @property
    def rubrics(self):
        '''list of all rubrics'''
        return Rubrics.query.all()

    @property
    def new_posts(self):
        '''list of last 5 posts,
        elements of list are models.Posts instances
        with all their attributes like title, content, etc.
        '''
        arc = ArchiveInfo()
        return arc

    @property
    def archive(self):
        '''list of all dates'''
        arc_list = ArchiveList()
        return arc_list


class ArchiveList():
    '''class that works like iterator. 
    Items are dates: str, sorted by date descending.

    simply pass the instance of it to the render_temlate function
    and use {% for el in instance %} construction'''
    
    _date_dict = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }

    def __getitem__(self, key):
        dates = self._refine_all_dates()
        return dates[key]

    def _get_all_dates(self) -> list:
        '''return list of all datetime.date objects from db ordered by date'''
        return Archive.query.order_by(desc(Archive.date)).all()

    def _refine_date(self, archive_date: date) -> str:
        '''makes recived date readable'''
        dt = archive_date.date
        readable_date = ArchiveList._date_dict[
            dt.strftime('%m')] + ' ' + dt.strftime('%Y')
        return readable_date

    def _refine_all_dates(self) -> list:
        '''applying refining function to all dates in the list making new one'''
        return [self._refine_date(date) for date in self._get_all_dates()]


class PostList():
    '''contains all information about rubric
    e.g. its title and list of posts with current rubric

    simply pass the instance of it to the render_temlate function
    and call property methods'''

    def __init__(self, slug) -> None:
        self._slug = slug

    def get_rubric(self) -> Rubrics:
        '''returns Rubrics instance by its slug'''
        return Rubrics.query.filter(Rubrics.slug == self._slug).first()

    def get_posts_by_rubric(self):
        '''returns list of Posts instancec with specific rubric_id'''
        return Posts.query.filter(Posts.rubric_id == self.get_rubric().id).all()

    @property
    def rubric(self) -> str:
        '''returns title of rubric'''
        return self.get_rubric().title

    @property
    def posts(self) -> list:
        '''returns list of Posts instancec'''
        return self.get_posts_by_rubric()
