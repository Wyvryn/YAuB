"""Database model definitions"""

from werkzeug.security import check_password_hash, generate_password_hash

from database import _Base, db
from flask.ext.login import UserMixin
from sqlalchemy import (Boolean, Column, DateTime, SmallInteger, String, Text,
                        desc, func)


class Config(_Base):
    __tablename__ = 'config'
    about = Column(Text)
    articlesperpage = Column(SmallInteger)
    blogname = Column(String(120))


class Article(_Base):
    __tablename__ = 'article'
    title = Column(String(120))
    imagecap = Column(String(100))
    banner = Column(String(100))
    author = Column(SmallInteger)
    content = Column(Text)
    short = Column(Text)
    published = Column(DateTime, default=func.now())
    isvisible = Column(Boolean)

    def __repr__(self):
        return ("<Article(title='%s', published='%s', isvisible='%s')>" %
                (self.title, self.published, self.isvisible and 'True' or 'False'))

    def tags(self):
        return db.session.query(ArticleTag).join(Article, ArticleTag.articleid == Article.rowid).filter(ArticleTag.articleid == self.rowid).all()

    def authorname(self):
        author = db.session.query(Author).filter(Author.rowid == self.author).first()
        return author and author.displayname or None


class ArticleTag(_Base):
    __tablename__ = 'articletag'
    articleid = Column(SmallInteger)
    tag = Column(String(25))

    def __repr__(self):
        return "<ArticleTag(articleid='%s', tag='%s')>" % (self.articleid, self.tag)


class Author(_Base, UserMixin):
    __tablename__ = 'author'
    username = Column(String(25))
    displayname = Column(String(50))
    password = Column(String(250))

    def __repr__(self):
        return ("<Author(username='%s', displayname='%s')>" %
                (self.username, self.displayname))

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.rowid

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)


class Blog(_Base):
    __tablename__ = 'blog'
    title = Column(String(50))


def getLatestArticles(number):
    return (
        db.session.query(Article)
        .order_by(Article.published.desc())
        .limit(number)
        .all()
    )


def getArticlesForPage(number, limit):
    return (
        db.session.query(Article)
        .order_by(Article.published.desc())
        .limit(limit)
        .offset((int(number) - 1) * limit)
        .all()
    )


def getArticlesWithTag(tag, number):
    return (
        db.session.query(Article)
        .join(ArticleTag, ArticleTag.articleid == Article.rowid)
        .filter(ArticleTag.tag == tag)
        .filter(Article.isvisible == True)
        .order_by(Article.published.desc())
        .limit(number)
        .all()
    )


def getArticle(id):
    return (
        db.session.query(Article)
        .filter(Article.rowid == id)
        .first()
    )


def topTags():
    return (
        db.session.query(ArticleTag.tag, func.count(ArticleTag.rowid).label('total'))
        .group_by(ArticleTag.tag)
        .order_by(desc('total'))
        .limit(10)
        .all()
    )


def updateTags(tags, articleID):
    """Helper method to handle updating tags"""

    aTags = ArticleTag.query.filter(ArticleTag.articleid == articleID)
    for aTag in aTags:
        db.session.delete(aTag)
    if tags:
        for tag in tags:
            aTag = ArticleTag()
            aTag.tag = tag
            aTag.articleid = articleID
            db.session.add(aTag)


def getAuthor(id):
    return (
        db.session.query(Author)
        .filter(Author.rowid == id)
        .first()
    )


def nextPage(pageNumber, limit):
    if len(getArticlesForPage(1, limit)) < limit:
        return None
    return len(getArticlesForPage(int(pageNumber) + 1, limit)) > 0


def getAbout():
    return db.session.query(Config).order_by(Config.rowid.desc()).first().about


def getArticlesPerPage():
    return db.session.query(Config).order_by(Config.rowid.desc()).first().articlesperpage


def getBlogName():
    return db.session.query(Config).order_by(Config.rowid.desc()).first().blogname


def getConfigObj():
    return db.session.query(Config).order_by(Config.rowid.desc()).first()


def hasSetupRun():
    """Returns True if we've run both the blog and author setup pages"""
    return db.session.query(Config).count() > 0 and db.session.query(Author).count() > 0
