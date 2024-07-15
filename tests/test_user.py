import unittest
from base_test import BaseTest
from controllers.main_controller import MainController
from models.user import User
from models.department import Department
import os


class TestUser(BaseTest):
    """
    TestUser class performs integration tests for user-related operations in the EpicEvents application.
    This includes creating, updating, and deleting collaborators.
    """

    def test_create_collaborator_as_management(self):
        """Test creating a collaborator as a management user."""

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Ensure the department for the new commercial user exists
        department_id = self.session.query(Department).filter_by(name="Gestion").first().id
        assert department_id is not None, "Gestion department does not exist"

        # Create a new collaborator
        result = MainController.create_collaborator(
            username="new_collaborator",
            password="password123",
            email="new_collaborator@example.com",
            name="New Collaborator",
            department_id=department_id,
        )
        print("Create collaborator result:", result)
        self.assertIn("successfully", result, "Failed to create collaborator")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.reopen_session()

        # Verify that the collaborator was created in the database
        collaborator = self.session.query(User).filter_by(email="new_collaborator@example.com").first()
        self.assertIsNotNone(collaborator, "Collaborator not found in the database")
        self.assertEqual(collaborator.username, "new_collaborator")
        self.assertEqual(collaborator.name, "New Collaborator")
        self.assertEqual(collaborator.department_id, department_id)

    def test_create_collaborator_as_commercial_should_fail(self):
        """Test creating a collaborator as a commercial user should fail."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Ensure the department for the new commercial user exists
        department_id = self.session.query(Department).filter_by(name="Commercial").first().id
        assert department_id is not None, "Commercial department does not exist"

        # Attempt to create a new collaborator (should fail)
        result = MainController.create_collaborator(
            username="commercial_collaborator",
            password="password123",
            email="commercial_collaborator@example.com",
            name="Commercial Collaborator",
            department_id=department_id,
        )
        print("Create collaborator result:", result)
        self.assertIn(
            "You are not authorized to perform this action.",
            result,
            "Commercial user should not be authorized to create a collaborator",
        )

        # Verify that the collaborator was not created in the database
        collaborator = self.session.query(User).filter_by(email="commercial_collaborator@example.com").first()
        self.assertIsNone(collaborator, "Collaborator should not be found in the database")

    def test_update_collaborator_as_management(self):
        """Test updating a collaborator as a management user."""

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Ensure the department for the new management user exists
        department_id = self.session.query(Department).filter_by(name="Gestion").first().id
        assert department_id is not None, "Gestion department does not exist"

        # Create a new collaborator
        MainController.create_collaborator(
            username="update_collaborator",
            password="password123",
            email="update_collaborator@example.com",
            name="Update Collaborator",
            department_id=department_id,
        )
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the collaborator was created
        collaborator = self.session.query(User).filter_by(email="update_collaborator@example.com").first()
        self.assertIsNotNone(collaborator, "Collaborator not found in the database")
        collaborator_id = collaborator.id

        # Update the collaborator
        result = MainController.update_collaborator(
            user_id=collaborator_id,
            username="updated_collaborator",
            email="updated_collaborator@example.com",
            name="Updated Collaborator",
        )
        print("Update collaborator result:", result)
        self.assertIn("successfully", result, "Failed to update collaborator")
        self.session.commit()

        # Reopen the session to check the database content
        self.reopen_session()

        # Verify that the collaborator was updated in the database
        updated_collaborator = self.session.query(User).filter_by(id=collaborator_id).first()
        self.assertIsNotNone(updated_collaborator, "Updated collaborator not found in the database")
        self.assertEqual(updated_collaborator.username, "updated_collaborator")
        self.assertEqual(updated_collaborator.email, "updated_collaborator@example.com")
        self.assertEqual(updated_collaborator.name, "Updated Collaborator")

    def test_delete_collaborator_as_management(self):
        """Test deleting a collaborator as a management user."""

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Ensure the department for the new management user exists
        department_id = self.session.query(Department).filter_by(name="Gestion").first().id
        assert department_id is not None, "Gestion department does not exist"

        # Create a new collaborator
        MainController.create_collaborator(
            username="delete_collaborator",
            password="password123",
            email="delete_collaborator@example.com",
            name="Delete Collaborator",
            department_id=department_id,
        )
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the collaborator was created
        collaborator = self.session.query(User).filter_by(email="delete_collaborator@example.com").first()
        self.assertIsNotNone(collaborator, "Collaborator not found in the database")
        collaborator_id = collaborator.id

        # Delete the collaborator
        result = MainController.delete_collaborator(collaborator_id)
        print("Delete collaborator result:", result)
        self.assertIn("successfully", result, "Failed to delete collaborator")
        self.session.commit()

        # Reopen the session to check the database content
        self.reopen_session()

        # Verify that the collaborator was deleted from the database
        deleted_collaborator = self.session.query(User).filter_by(id=collaborator_id).first()
        self.assertIsNone(deleted_collaborator, "Collaborator should not be found in the database")

    def test_delete_collaborator_as_commercial_should_fail(self):
        """Test deleting a collaborator as a commercial user should fail."""

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Ensure the department for the new management user exists
        department_id = self.session.query(Department).filter_by(name="Gestion").first().id
        assert department_id is not None, "Gestion department does not exist"

        # Create a new collaborator
        MainController.create_collaborator(
            username="fail_delete_collaborator",
            password="password123",
            email="fail_delete_collaborator@example.com",
            name="Fail Delete Collaborator",
            department_id=department_id,
        )
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the collaborator was created
        collaborator = self.session.query(User).filter_by(email="fail_delete_collaborator@example.com").first()
        self.assertIsNotNone(collaborator, "Collaborator not found in the database")
        collaborator_id = collaborator.id

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Attempt to delete the collaborator (should fail)
        result = MainController.delete_collaborator(collaborator_id)
        print("Delete collaborator result:", result)
        self.assertIn(
            "You are not authorized to perform this action.",
            result,
            "Commercial user should not be authorized to delete a collaborator",
        )
        self.session.commit()

        # Verify that the collaborator was not deleted from the database
        collaborator = self.session.query(User).filter_by(id=collaborator_id).first()
        self.assertIsNotNone(collaborator, "Collaborator should still be found in the database")


if __name__ == "__main__":
    unittest.main()
