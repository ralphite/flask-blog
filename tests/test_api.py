__author__ = 'yawen'

import unittest

from flask import url_for, json
from base64 import b64encode
from app import create_app, db
from app.models import Role, User, Post


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')
            ).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_no_auth(self):
        resp = self.client.get(url_for('api.get_posts'),
                               content_type='application/json')
        self.assertTrue(resp.status_code == 401)

    def test_posts(self):
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='j@j.com', password='c', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        resp = self.client.post(url_for('api.new_post'),
                                headers=self.get_api_headers('j@j.com', 'c'),
                                data=json.dumps({
                                    'body': 'body of the *blog* post'}))
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get('Location')
        self.assertIsNotNone(url)

        resp = self.client.get(
            url,
            headers=self.get_api_headers('j@j.com', 'c')
        )
        self.assertTrue(resp.status_code == 200)
        json_resp = json.loads(resp.data.decode('utf-8'))
        self.assertTrue(json_resp['url'] == url)
        self.assertTrue(json_resp['body'] == 'body of the *blog* post')
        self.assertTrue(json_resp['body_html'] ==
                        '<p>body of the <em>blog</em> post</p>')

    def test_comments(self):
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='j@j.com', password='c', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # post a post
        resp = self.client.post(url_for('api.new_post'),
                                headers=self.get_api_headers('j@j.com', 'c'),
                                data=json.dumps({
                                    'body': 'body of the *blog* post'}))
        self.assertTrue(resp.status_code == 201)

        # post a comment
        post = Post.query.filter_by(body='body of the *blog* post').first()
        resp = self.client.post(url_for('api.post_post_comment', post_id=post.id),
                                headers=self.get_api_headers('j@j.com', 'c'),
                                data=json.dumps({
                                    'body': 'body of the *comment*'}))
        self.assertTrue(resp.status_code == 201)

        # get comments of a post
        resp = self.client.get(url_for('api.get_post_comments', post_id=post.id),
                               content_type='application/json',
                               headers=self.get_api_headers('j@j.com', 'c'))
        self.assertTrue(resp.status_code == 200)
        json_resp = json.loads(resp.data.decode('utf-8'))
        #print json_resp['comments'][0]
        self.assertTrue(json_resp['comments'][0]['body'] == 'body of the *comment*')