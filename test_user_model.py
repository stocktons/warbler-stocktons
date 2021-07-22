"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from inspect import unwrap
import os
from re import U # what is this?
from unittest import TestCase

from app import IntegrityError
from sqlalchemy import exc

from models import db, User, Message, Follows, Bcrypt
bcrypt = Bcrypt()

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

USER1_DATA = {
    "email" : "test@test.com",
    "username" : "testuser",
    "password" : "HASHED_PASSWORD",
    "image_url" : "",
}

USER2_DATA = {
    "email" : "test2@test.com",
    "username" : "testuser2",
    "password" : "HASHED_PASSWORD",
    "image_url" : "",
}

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup(**USER1_DATA)
        user2 = User.signup(**USER2_DATA)
        
        db.session.add_all([user1, user2])
        db.session.commit()

        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2
        
    def tearDown(self):
        """Clean up fouled transactions."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = self.user1

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_repr(self):
        """Does the repr work?"""

        u = self.user1
        test_user_id = u.query.get(u.id)

        self.assertEqual(f"{test_user_id}", f"<User #{u.id}: {u.username}, {u.email}>")


    def test_is_following(self):
        """Is user1 (Fran) following user2 (Bob)?"""

        u1 = self.user1
        u2 = self.user2

        u1.following.append(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)

    def test_is_not_following(self):
        """Is user1 NOT following user2?"""

        u1 = self.user1
        u2 = self.user2

        self.assertEqual(u1.is_following(u2), False)
    
    
    def test_is_followed_by(self):
        """Is user1 (Fran) followed by user2 (Bob)? """
        
        u1 = self.user1
        u2 = self.user2
        
        u1.followers.append(u2)
        db.session.commit()
        
        self.assertEqual(u1.is_followed_by(u2), True)

    def test_is_not_followed_by(self):
        """Is user1 NOT following user2?"""
    
        u1 = self.user1
        u2 = self.user2
        
        self.assertEqual(u1.is_followed_by(u2), False)


    def test_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""
        
        test_user = User.signup("testuser3", "testuser3@test.com", "password", "")

        db.session.commit()
        
        test_user_obj = User.query.get(test_user.id)
        
        self.assertEqual(test_user_obj.username, "testuser3")
        self.assertEqual(test_user_obj.email, "testuser3@test.com")
        self.assertEqual(test_user_obj.password, test_user.password) 
        # why is this working ???
            
        
    def test_invalid_signup(self):
        """Does User.signup fail to create a new user if given invalid credentials?"""
        
        User.signup("testuser", "testuser@test.com", "password", "")
                
        # integrity error is the related to database (repeated data)
        # with self.assertRaises(exc.IntegrityError) :
        #     db.session.commit()
        
        self.assertRaises(exc.IntegrityError, db.session.commit)
        
    def test_invalid_password(self):
        """Does User.signup fail to create a new user if given empty password?"""

        with self.assertRaises(ValueError): 
            User.signup("testuser", "testuser@test.com", "", "")

  
    def test_signin(self):
        """Does User.authenticate successfully return a user given valid username and password?"""

        test_user = User.authenticate(self.user1.username, USER1_DATA["password"])
    
        self.assertTrue(test_user)
       
    


        
        