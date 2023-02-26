from mock_db_data import MockDB
from mock import patch
import unittest
import db_utils_data

class TestUtils(MockDB):
    def test_db_write(self):
        with self.mock_db_config:
            for table in ["ccf_data_full", "ccf_data_partial", "ccf_data_i", "ccf_data_to_add", "ccf_data_remaining"]:
                print("111")
                self.assertEqual(db_utils_data.db_write(f"""INSERT INTO `{table}` (`distance_from_home`, `distance_from_last_transaction`, `ratio_to_median_purchase_price`, `repeat_retailer`, `used_chip`, `used_pin_number`, `online_order`, `fraud`) VALUES
                                (3.141526, 3.141526, 3.1415, 1, 0, 1, 0, 1)"""), True, "Couldn't add value in the good format")
                print("222")
                #self.assertEqual(db_utils_data.db_write(f"""INSERT INTO `{table}` (`distance_from_home`, `distance_from_last_transaction`, `ratio_to_median_purchase_price`, `repeat_retailer`, `used_chip`, `used_pin_number`, `online_order`, `fraud`) VALUES
                #               ('Bonjour', 'Mon', 'Nom', 'Est', 'Dagobert','Le', 'Gentil', 'Chien')"""), False, "Same username was added twice but not permitted ")
                #self.assertEqual(db_utils_data.db_write(f"""INSERT INTO `ccf_data_full` (`id`, `username`, `password_hash`) VALUES
                 #               ('1', 'user', 'hashed_pswd')"""), False, "the id is not incremented")
                print("333")
                self.assertEqual(db_utils_data.db_write(f"""DELETE FROM `{table}` WHERE ROUND(distance_from_home, 4)=ROUND(3.1415326, 4) AND ROUND(distance_from_last_transaction, 4)=ROUND(3.1415326, 4);"""), True, "couldn't remove random user")
                #self.assertEqual(db_utils.db_write("""DELETE FROM `user WHERE id='3' """), True)
                # Other tests can be added bellow 
if __name__ == "__main__":
    unittest.main()