__author__ = 'yawen'

import re
import time
import unittest
import threading
from selenium import webdriver

from app import create_app, db
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='john@example.com', username='john', password='cat',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!', self.client.page_source))
        self.client.find_element_by_link_text('Sign In').click()
        self.assertTrue('Login' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('john@example.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        #time.sleep(10000)
        self.assertTrue('Hello' in self.client.page_source)

        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('Edit' in self.client.page_source)
        self.client.find_element_by_link_text('Followers').click()
        time.sleep(10000)
        self.client.find_element_by_link_text('Moderate Comments').click()
        self.client.find_element_by_link_text('Profile').click()
        self.client.find_element_by_link_text('Following').click()
        self.client.find_element_by_link_text('Edit Profile').click()