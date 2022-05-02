from typing import Union
from datetime import date

from sqlalchemy import desc

from models import Archive, Posts, Rubrics, db
from forms import SearchForm


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

    @staticmethod
    def get_date_id(date: date) -> int:
        '''
        if there is no dates in database or recieved date not in database
        then add self.date to DB
        returns id of recived date
        '''
        last = Archive.query.order_by(desc(Archive.id)).first()
        if last is None:
            AddPost._archive_add(date)
            return 1
        post_date = Archive.query.filter(Archive.date == date).first()
        if post_date is None:
            AddPost._archive_add(date)
            return last.id + 1
        return post_date.id

    @staticmethod
    def _archive_add(date: date) -> None:
        '''add to database recived date'''
        archive = Archive(date=date)
        add_to_db(archive)

    def _post_add(self) -> None:
        '''add post with correct date and rubric id to database'''
        date_id = self.get_date_id(self.date)
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
        dates = self._remove_duplicates()
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
        return [(self._refine_date(date), date.date) for date in self._get_all_dates()]
    
    def _remove_duplicates(self) -> list:
        '''removes all duplicates in list of tuples'''
        dates = self._refine_all_dates()
        new_dates = []
        i = 0
        while i < len(dates)-1:
            new_dates.append(dates[i])
            if dates[i][0] == dates[i+1][0]:
                for j in range(i+1, len(dates)-1):

                    if dates[j][0] != dates[j+1][0]:
                        i = j
                        break
            else:
                if i == len(dates)-2: # if last one is not the same as previous add to new list
                    new_dates.append(dates[i+1])
            i += 1
                    
        return new_dates
            
            


class SidebarInfo():
    '''three property functions contains all information
    that needs to be displayed at sidebar throughout all web-site

    simply pass the instance of it to the render_temlate function
    and call property methods'''

    @property
    def rubrics(self) -> list:
        '''list of all rubrics'''
        return Rubrics.query.all()

    @property
    def new_posts(self) -> ArchiveInfo:
        '''list of last 5 posts,
        elements of list are models.Posts instances
        with all their attributes like title, content, etc.
        '''
        arc = ArchiveInfo()
        return arc

    @property
    def archive(self) -> ArchiveList:
        '''list of all dates'''
        arc_list = ArchiveList()
        return arc_list
    
    @property
    def get_form(self) -> SearchForm:
        form = SearchForm()
        return form


class PostList():
    '''contains all information about rubric
    e.g. its title and list of posts with current rubric

    simply pass the instance of it to the render_temlate function
    and call property methods'''

    def __init__(self, slug:str) -> None:
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


class PostsFromArchive():
    def __init__(self, year: int, month:Union[int, None] = None) -> None:
        self.year = year
        self.month = month
    
    def _get_posts_by_year(self) -> list:
        return db.engine.execute(
            SearchPost.SEARCH_POST_TEMPLATE +
            f'WHERE year(archive.date)={self.year};').all()
    
    def get_posts_by_year_and_month(self) -> list:
        if self.month is None:
            return self._get_posts_by_year()
        return db.engine.execute(
            SearchPost.SEARCH_POST_TEMPLATE +
            f'WHERE year(archive.date)={self.year} AND month(archive.date)= {self.month};').all()


class SearchPost():
    
    SEARCH_POST_TEMPLATE = f'''SELECT posts.title, posts.slug, posts.content, rubrics.title AS ttl, archive.date, rubrics.slug AS slg
            FROM posts 
            JOIN archive ON posts.date_id = archive.id 
            JOIN rubrics ON posts.rubric_id = rubrics.id '''
    
    def __init__(self, keyword:str) -> None:
        self._keyword = keyword

    def get_post_by_keyword(self) -> Union[list, None]:
        return db.engine.execute(
            self.SEARCH_POST_TEMPLATE + f'WHERE posts.title LIKE "%{self._keyword}%" OR posts.content LIKE "%{self._keyword}%";'
        )
    
class MainArticle():
    MAIN_ARTICLE_ID = 1
    ABOUT_ARTICLE_ID = 2
    SOFTWARE_ARTICLE_ID = 3
    CONTACTS_ARTICLE_ID = 4
