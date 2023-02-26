from mock_db_authentication import MockDB
from mock import patch
import unittest
import db_utils_authentication

class TestUtils(MockDB):
    def test_db_write(self):
        with self.mock_db_config:
            self.assertEqual(db_utils_authentication.db_write("""INSERT INTO ccf_mysql.user (`id`, `username`, `password_hash`) VALUES
                            ('1', 'admin', '$2b$12$.JtAneBODWfF29sdJbCgceK8UKjISRSki3vHRIP7OMyk.xsTO49NG')"""), False, "smothing wrong cause we Could create the user admin with id = 1")
#                            # Hashed => 4dm1N
            self.assertEqual(db_utils_authentication.db_write("""INSERT INTO ccf_mysql.user (`id`, `username`, `password_hash`) VALUES
                            ('2', 'admin', 'admin')"""), False, "Same username was added twice but not permitted ")
            self.assertEqual(db_utils_authentication.db_write("""INSERT INTO ccf_mysql.user (`id`, `username`, `password_hash`) VALUES
                            ('1', 'user', 'hashed_pswd')"""), False, "the id is not incremented")
            self.assertEqual(db_utils_authentication.db_write("""DELETE FROM ccf_mysql.user WHERE id='3' """), True, "couldn't remove random user")
            self.assertEqual(db_utils_authentication.db_write("""DELETE FROM ccf_mysql.user WHERE id='4' """), True, "couldn't remove random user")
            #self.assertEqual(db_utils_authentication.db_write("""DELETE FROM `user WHERE id='3' """), True)
            # Other tests can be added bellow 
if __name__ == "__main__":
    unittest.main()
