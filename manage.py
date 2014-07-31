import os

from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


COV = None
if os.environ.get('FLASK_BLOG_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,
                Post=Post, Follow=Follow, Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the Unit tests."""
    if coverage and not os.environ.get('FLASK_BLOG_COVERAGE'):
        import sys
        os.environ['FLASK_BLOG_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Code coverage:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML result: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def recreate_data():
    """Generate fake data for development and testing"""
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


@manager.command
def profile(length=10, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role, User

    upgrade()
    Role.insert_roles()
    User.add_self_follows()


if __name__ == '__main__':
    manager.run()