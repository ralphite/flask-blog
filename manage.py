import os

from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Post=Post,
                Follow=Follow, Comment=Comment)


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
    print 'dropping existing tables...'
    db.drop_all()
    print 'creating tables...'
    db.create_all()
    print 'inserting roles...'
    Role.insert_roles()
    print 'creating admin user...'
    u1 = User(username='ralph', email='ralph.wen@gmail.com', password='r',
              name='Ralph Wen', location='Hangzhou, China',
              about_me='This is the creator of everything', confirmed=True)
    db.session.add(u1)
    print 'creating moderate user...'
    u2 = User(username='yadong', email='wenyadong@gmail.com', password='r',
              name='Yadong Wen', location='Hangzhou, China',
              about_me='Yeah', confirmed=True)
    db.session.add(u2)
    db.session.commit()
    print 'generating 50 normal users...'
    User.generate_fake(50)
    print 'generating 500 posts...'
    Post.generate_fake(500)
    print 'generating follows...'
    User.generate_following()
    print 'generating comments...'
    Comment.generate_comments()
    print '...done'


if __name__ == '__main__':
    manager.run()