"""
Main webapp logic
All setup config and endpoint definitions are stored here


.. TODO:: allow user creation
.. TODO:: page to show loaded plugins

"""

from dateutil import parser

import models
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user)
from flask_uploads import IMAGES, UploadNotAllowed, UploadSet
from forms import ArticleForm, AuthorForm, ConfigForm, LoginForm
from markdown2 import Markdown
from utils import flash_errors, load_plugins

markdowner = Markdown()
login_manager = LoginManager()
uploaded_photos = UploadSet('photos', IMAGES)

plugs, header_includes, footer_includes = load_plugins()

main = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(id):
    return models.getAuthor(int(id))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("main.home")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("login.html", form=form, models=models)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out.')
    return redirect(url_for('main.home'))


@main.route("/<int:page>")
@main.route("/", defaults={'page': 1})
def home(page):
    """Home Page
    We have two routes - / and /<int:page>
    If we're giving a specific page to load, get articles for that page
    Otherwise, load page 1"""

    if not models.hasSetupRun():
        return redirect(url_for('main.initial_setup_user'))
    articlesPerPage = models.getArticlesPerPage()
    nextPage = models.nextPage(page, articlesPerPage)
    return render_template(
        'home.html',
        header_includes=header_includes,
        footer_includes=footer_includes,
        models=models,
        entries=models.getArticlesForPage(page, articlesPerPage),
        sidebar=True,
        pageNumber=int(page),
        nextPage=nextPage)


@main.route('/firstrun/blog', methods=['GET', 'POST'])
def initial_setup_blog():
    """Initial blog setup when accessing the YAuB for the first time"""

    if models.hasSetupRun():
        """Only run setup once"""
        return redirect(url_for('main.home'))

    obj = models.Config()
    form = ConfigForm(obj=obj)

    if request.method == "POST" and form.validate():
        form.populate_obj(obj)
        models.db.session.add(obj)
        models.db.session.commit()
        flash('Successfully set blog settings')
        return redirect(url_for("main.home"))
    else:
        flash_errors(form)

    return render_template('admin_blog.html', form=form, firstrun=True)


@main.route('/firstrun/author', methods=['GET', 'POST'])
def initial_setup_user():
    """Initial user setup when accessing YAuB for the first time"""

    if models.hasSetupRun():
        """Only run setup once"""
        return redirect(url_for('main.home'))

    obj = models.Author()
    form = AuthorForm(obj=obj)

    if request.method == "POST" and form.validate():
        form.populate_obj(obj)
        obj.set_password(form.password.data)
        models.db.session.add(obj)
        models.db.session.commit()
        flash('Successfully created user')
        return redirect(url_for("main.initial_setup_blog"))
    else:
        flash_errors(form)

    return render_template('firstrun_author.html', form=form, firstrun=True)


@main.route("/admin/settings", methods=['GET', 'POST'])
@login_required
def admin_blog():
    """Page to change YAuB settings"""
    obj = models.getConfigObj()
    form = ConfigForm(obj=obj)
    # populate the form with our blog data

    if request.method == "POST" and form.validate():
        form.populate_obj(obj)
        models.db.session.commit()
        flash('Successfully editted blog settings')
        return redirect(url_for("main.home"))
    else:
        flash_errors(form)
    return render_template('admin_blog.html', form=form, models=models)


@main.route("/admin/article", defaults={'id': None}, methods=['GET', 'POST'])
@main.route("/admin/article/<id>", methods=['GET', 'POST'])
@login_required
def admin_article(id):
    """Page to create or edit an article
    If no article id is given we will create a new article,
    Otherwise we edit the article at the given id"""

    isNew = not id
    if isNew:
        obj = models.Article()
    else:
        obj = models.getArticle(int(id))

    obj.author = current_user.rowid

    form = ArticleForm(obj=obj)

    if not isNew:
        # Bootstrap-TagsInput hooks into a select multiple field
        form.tags.choices = [
            (a.tag, a.rowid)
            for a in models.ArticleTag.query.filter(
                models.ArticleTag.articleid == int(id)
            ).order_by('tag')
        ]
    else:
        form.tags.choices = []

    if request.method == "POST" and form.validate():
        form.populate_obj(obj)
        if 'imgcap' in request.files:
            try:
                filename = uploaded_photos.save(request.files['imgcap'])
                obj.imagecap = filename
            except UploadNotAllowed:
                # If no picture is passed, don't crash
                pass
        if 'banner' in request.files:
            try:
                filename = uploaded_photos.save(request.files['banner'])
                obj.banner = filename
            except UploadNotAllowed:
                # If no picture is passed, don't crash
                pass

        obj.published = parser.parse(obj.published)
        if isNew:
            models.db.session.add(obj)

        models.db.session.flush()
        models.updateTags(obj.tags, obj.rowid)
        models.db.session.commit()
        flash('Successfully editted article')
        return redirect(url_for("main.home"))

    return render_template('admin_article.html', form=form, rowid=id, models=models)


@main.route("/admin/delete/<id>", methods=['GET', 'POST'])
@login_required
def admin_delete(id):
    """Deletes an article at a given id"""

    obj = models.getArticle(int(id))
    models.updateTags(None, int(id))
    models.db.session.delete(obj)
    models.db.session.commit()
    flash('Successfully deleted article')
    return redirect(url_for("main.home"))


@main.route("/admin/author", methods=['GET', 'POST'])
@login_required
def admin_author():
    """Updates author info"""

    obj = models.getAuthor(int(current_user.rowid))
    # Hold on to this until we validate the fields from the form
    password = models.getAuthor(int(current_user.rowid)).password
    form = AuthorForm(obj=obj)
    # populate the form with our blog data

    if request.method == "POST" and form.validate():
        form.populate_obj(obj)
        if len(form.password.data) == 0:
            # If the password field has no data, don't change the user's password
            obj.password = password
        else:
            obj.set_password(form.password.data)
        models.db.session.commit()
        flash('Successfully editted user info')
        return redirect(url_for("main.home"))
    else:
        flash_errors(form)
    return render_template('admin_author.html', form=form, models=models)


@main.route("/article/<id>")
def article(id):
    """Display an article with a given id"""

    article = models.getArticle(id)
    markdown = article.content
    markdown = markdown.replace('\\n', '<br />')
    html = markdowner.convert(markdown)

    # Run any plugins on our html before passing it to the template
    for plug in plugs:
        html = plug.run(html)

    return render_template(
        'article.html',
        header_includes=header_includes,
        footer_includes=footer_includes,
        html=html,
        article=article,
        models=models,
        sidebar=True
    )


@main.route("/tag/<id>")
def tag(id):
    """Loads the main page but only shows articles that have a given tag"""

    return render_template(
        'home.html',
        header_includes=header_includes,
        footer_includes=footer_includes,
        entries=models.getArticlesWithTag(id, 10),
        models=models,
        sidebar=True
    )
