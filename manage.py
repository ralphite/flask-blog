import os

from app import create_app, db
from app.models import User, Role, Permission, Post

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Post=Post)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the Unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_data():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    u1 = User(username='ralph', email='ralph.wen@gmail.com', password='r',
              name='Ralph Wen', location='Hangzhou, China',
              about_me='This is the creator of everything', confirmed=True)
    db.session.add(u1)
    u2 = User(username='yadong', email='wenyadong@gmail.com', password='r',
              name='Yadong Wen', location='Hangzhou, China',
              about_me='Yeah', confirmed=True)
    db.session.add(u2)
    db.session.commit()
    User.generate_fake(50)
    Post.generate_fake(500)


if __name__ == '__main__':
    manager.run()