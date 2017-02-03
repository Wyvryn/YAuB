"""Manager Module for YAuB
Creates the app and then runs it with Flask-Script
`python manage.py runserver` will start the webapp
"""

from flask.ext.script import Manager
from flask_migrate import MigrateCommand

from YAuB import create_app

app = create_app('YAuB.config.Config')
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
