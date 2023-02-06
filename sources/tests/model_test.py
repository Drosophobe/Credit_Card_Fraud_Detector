import unittest
import sys
sys.path.append('/Users/pierresarzier/Credit_Card_Fraud/sources/FastAPI')
from Fraud import Fraud

###########################################MODEL####################################################
class TestEncryption(unittest.TestCase):
    def setUp(self):
    # data to test
        self.my_features = [1., 2., 3., 4., 5., 6., 7]
    # tests go bellow:
    def test_inputExists(self):
        # Check if the input exists 
        self.assertIsNotNone(self.my_features, "The input doesn't exist")
    def test_inputType(self):
        # Check the type of the input (list)
        self.assertIsInstance(self.my_features, list, "The model expects list but : {} was passed".format(type(self.my_features)))
    def test_fraud_ReturnsSomething(self):
        # Check is the model return something
        self.assertIsNotNone(Fraud(self.my_features), "The model doesn't return anything")
    def test_lenTest(self):
        # Check is len(my_features) match with expected len
        self.assertEqual(len(self.my_features), 7, "The model needs 7 features : {} were passed".format(len(self.my_features)))
    def test_inputType(self):
        # Check the type of the output (str)
        self.assertIsInstance(Fraud(self.my_features), str, "The model's output is expected to be a string but : {} is sent".format(type(Fraud(self.my_features))))
    def test_inputsType(self):
        # If the type of each items in the array match the requirement (int or float)
        for i in range(len(self.my_features)):
            self.assertIsInstance(self.my_features[i], float|int, f"The feature n°{i+1} is not a float")

if __name__ == "__main__":
    unittest.main()