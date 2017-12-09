import unittest
import json
from app import create_app, db
from app.models import Category, User, Recipe

class CategoryTestCase(unittest.TestCase):
    """This class represents the category test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'name': 'supper'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)


    def test_accessing_category_view_with_invalid_or_expired_token(self):
        """ Tests accessing the category endpoint with an invalid
        or expired token """
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        response = self.client().get('/categories/',
                                  headers=dict(Authorization="Bearer " + 'XBA5567SJ2K119'))
        self.assertEqual(response.status_code, 401)
    def test_category_creation(self):
        """Test the API can create a category (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('supper', str(res.data))

    def test_api_can_get_all_categories(self):
        """Test API can get a category (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        # get all the categories that belong to the test user by making a GET request
        res = self.client().get(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('supper', str(res.data))

    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the category is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('supper', str(result.data))

    def test_category_can_be_edited(self):
        """Test API can edit an existing category. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a category by making a POST request
        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'lunch, supper'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the category
        results = json.loads(rv.data.decode())

        # then, we edit the created category by making a PUT request
        rv = self.client().put(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "dinner, dissert :-)"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited category to see if it is actually edited.
        results = self.client().get(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('dinner', str(results.data))

    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'lunch'})
        self.assertEqual(rv.status_code, 201)
        # get the category in json
        results = json.loads(rv.data.decode())

        # delete the category we just created
        res = self.client().delete(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()