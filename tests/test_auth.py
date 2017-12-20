
import unittest
import json
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "You registered successfully. Please login.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")


    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login', data=not_a_user)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message 
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")
    def test_user_registers_with_valid_email(self):
        """Test for invalid email and password on registration"""
        user={
            "email":"hadijah", "password":"123"
        }
        res = self.client().post('/api/v1/auth/register', data=user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code,400)
        self.assertEqual(
            result['message'], 'Invalid email or password, Please try again with a valid email and a password with morethan 6 characters')
    
    def test_password_reset(self):
        """Test API for password reset (Post request)"""
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=self.user_data)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        new_data = {'email':'test@example.com', 'password':'test_password','new_password': 'test12345'}
        res = self.client().post('/api/v1/auth/reset_password', headers=dict(Authorization=
                "Bearer " + access_token), data=new_data)
        self.assertEqual(res.status_code, 200)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "Your password has been reset.")

    def test_user_logout(self):
        """ Test a user can logout from the session"""
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=self.user_data)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res = self.client().post('/api/v1/auth/logout', headers=dict(
            Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode())
        self.assertTrue(data['message'] == 'Your have been logged out.')
        
