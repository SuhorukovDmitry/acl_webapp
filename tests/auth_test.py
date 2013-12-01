import re
from base import BaseTest


class RegisterBaseTest(BaseTest):
    def post_register_xsrf(self, data, is_ajax=False):
        reg_url = self.reverse_url('register')
        resp = self.get(reg_url)
        # add xsrf to post request
        data['_xsrf'] = re.search(
            '<input type="hidden" name="_xsrf" value="(.*?)"', resp.body)\
            .group(1)
        if is_ajax:
            return self.post_ajax(reg_url, data=data)
        else:
            return self.post(reg_url, data=data)

    def assertUserExist(self, email):
        user = self.db_find_one('accounts', {'_id': email})
        self.assertEqual(user['_id'], email)

    def assertUserNotExist(self, email):
        user = self.db_find_one('accounts', {'_id': email})
        self.assertEqual(user, None)

    def assertJsonSuccess(self, json_data):
        self.assertTrue(json_data['result'])

    def assertJsonFail(self, json_data):
        self.assertFalse(json_data['result'])

    @property
    def valid_email(self):
        return 'vasya@vasya.com'

    @property
    def invalid_email(self):
        return 'bad_email'


class RegisterTestHtml(RegisterBaseTest):

    def test_page_exist(self):
        return self.page_exist('register')

    def test_user_is_created(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data)
        # check we are redirected to home page
        self.assertEqual(resp.code, 302)
        self.assertEqual(resp.headers['Location'], self.reverse_url('home'))
        self.assertUserExist(self.valid_email)

    def test_password_mismatch(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': 'notequal',
        }
        resp = self.post_register_xsrf(post_data)
        # check, repsponse is not redirect
        self.assertEqual(resp.code, 200)
        self.assertUserNotExist(self.valid_email)

    def test_bad_email(self):
        post_data = {
            'email': self.invalid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data)
        # check, repsponse is not redirect
        self.assertEqual(resp.code, 200)
        self.assertUserNotExist(self.invalid_email)

    def test_duplicated_email(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data)
        self.assertEqual(resp.code, 302)
        self.clear_cookie()
        # try to create user with same email
        resp = self.post_register_xsrf(post_data)
        self.assertEqual(resp.code, 200)
        # only one user in database
        users = self.db_find('accounts', {'_id': self.valid_email})
        self.assertEqual(len(users), 1)

    def test_no_xsrf(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        reg_url = self.reverse_url('register')
        resp = self.post(reg_url, data=post_data)
        # Forbidden
        self.assertEqual(resp.code, 403)


class RegisterTestAjax(RegisterBaseTest):

    def test_resourse_exist(self):
        resp = self.get_ajax(self.reverse_url('register'))
        self.assertEqual(resp.code, 200)

    def test_user_is_created(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonSuccess(resp_data)
        self.assertUserExist(self.valid_email)
        self.assertEqual(resp_data['redirect_url'], self.reverse_url('home'))

    def test_password_mismatch(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': 'notequal',
        }
        resp = self.post_register_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertUserNotExist(self.valid_email)

    def test_bad_email(self):
        post_data = {
            'email': self.invalid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertUserNotExist(self.invalid_email)

    def test_duplicated_email(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_register_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonSuccess(resp_data)
        self.clear_cookie()
        # try to create user with same email
        resp = self.post_register_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        # only one user in database
        users = self.db_find('accounts', {'_id': self.valid_email})
        self.assertEqual(len(users), 1)

    def test_no_xsrf(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        reg_url = self.reverse_url('register')
        resp = self.post_ajax(reg_url, data=post_data)
        # Forbidden
        self.assertEqual(resp.code, 403)


class LoginTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('login')