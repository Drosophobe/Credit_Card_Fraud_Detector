from mock_db import MockDB
from mock import patch
import unittest
import db_utils

class TestUtils(MockDB):
    def test_db_write(self):
        with self.mock_db_config:
            self.assertEqual(db_utils.db_write("""INSERT INTO `user` (`id`, `username`, `password_hash`) VALUES
                            ('3', 'Dagobert_1', 'qdeqqdwqe')"""), True)
            self.assertEqual(db_utils.db_write("""INSERT INTO `user` (`id`, `username`, `password_hash`) VALUES
                            ('1', 'Dagobert_2', 'qdeqqdwqe')"""), False)
            self.assertEqual(db_utils.db_write("""DELETE FROM `user` WHERE id='1' """), True)
            #self.assertEqual(db_utils.db_write("""DELETE FROM `user WHERE id='3' """), True)
if __name__ == "__main__":
    unittest.main()