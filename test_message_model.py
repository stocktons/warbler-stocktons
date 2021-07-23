"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os

from unittest import TestCase

from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows, Bcrypt
bcrypt = Bcrypt()

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"
# how to check or set environmental variables (shell variables)

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

class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # Follows.query.delete()
        # Message.query.delete()
        User.query.delete()

        user1 = User.signup(**USER1_DATA)
        user2 = User.signup(**USER2_DATA)
        
        db.session.add_all([user1, user2])
        db.session.commit()

        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2
        
        m1 = Message(text="user1 message", user_id=self.user1.id)
        m2 = Message(text="user2 message", user_id=self.user2.id)
        
        self.m1 = m1
        self.m2 = m2
        
        db.session.add_all([m1, m2])
        db.session.commit()
        
    def tearDown(self):
        """Clean up fouled transactions."""

        res = super().tearDown()
        db.session.rollback()
        return res

    
    def test_message_model(self):
        """Does basic model work?"""
        
        message = Message(text="test message", user_id=self.user1.id)
        
        db.session.add(message)
        db.session.commit()
        
        self.assertEqual(len(self.user1.messages), 2)
        
    
    def test_liked_message(self):
        """Does it successfully show user1 has liked user2's message? """
        
        self.user1.likes.append(self.m2)
        
        db.session.commit()
        
        self.assertIn(self.m2, self.user1.likes)
        
    
    def test_not_liked_message(self):
        """Does it successfully show user2 has NOT liked user1's message? """
        
        self.assertNotIn(self.m1, self.user2.likes)
        
    
    # def test_like_own_message(self):
    #     """Tests that user cannot like their own message(s)"""
        # create a method on the model that returns false if user tries to like own message
        
        # list comprehension over likes that finds the users
        