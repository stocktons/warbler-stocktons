"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        
        self.testuser = User.query.filter_by(username=testuser.username).first()
        # prevent detached instance error
    
    def test_follower(self):
        """Test showing follower pages for any user when logged in?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            resp = c.get(f'/users/{self.testuser.id}/followers')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.testuser.username}', html)
            
    
    def test_following(self):
        """Test following pages for any user when logged in?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            resp = c.get(f'/users/{self.testuser.id}/following')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.testuser.username}', html)
            
    
    # add additional users
    
    # create followers for users
    #   do some following
    #   test that that user should be showing up on the respective pages 
    
    # create followers helper function
    
    
    # can't like or unlike without being authenticated
    # reverse logic
    
    
    # can't follow without being authenticated
    # reverse logic