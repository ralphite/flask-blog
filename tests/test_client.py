__author__ = 'yawen'

import unittest, re
from flask import url_for
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        resp = self.client.get(url_for('main.index'))
        self.assertTrue('Stranger' in resp.get_data(as_text=True))

    def test_register_and_login_logout(self):
        resp = self.client.post(url_for('auth.register'), data={
            'email': 'john@example.com',
            'username': 'john',
            'name': 'John',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertTrue(resp.status_code == 302)

        resp = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        data = resp.get_data(as_text=True)
        self.assertTrue('not confirmed' in data)

        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_confirmation_token()
        resp = self.client.get(url_for('auth.confirm', token=token),
                               follow_redirects=True)
        data = resp.get_data(as_text=True)
        #print data
        self.assertTrue('Thanks for confirming' in data)

        resp = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = resp.get_data(as_text=True)
        #print data
        self.assertTrue('logged out' in data)