"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from inspect import unwrap
import os
from re import U # what is this?
from unittest import TestCase

from models import db, User, Message, Follows

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
    "password" : "HASHED_PASSWORD"
}

USER2_DATA = {
    "email" : "test2@test.com",
    "username" : "testuser2",
    "password" : "HASHED_PASSWORD"
}

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(**USER1_DATA)
        user2 = User(**USER2_DATA)
        db.session.add_all([user1, user2])
        db.session.commit()

        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2

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