import unittest 
import Fraud 

class Test(unittest.TestCase):
    """
    Tests of Fraud.py functions
    """

    def test_Fraud(self):
        """
        Must return 'Fraud' with the following inputs
        A=[4.158589,0.079312,8.314564,1,0,0,1]
        """
        A=[4.158589,0.079312,8.314564,1,0,0,1]
        self.assertEqual(Fraud(A),'Fraud')

    def test_no_Fraud(self):
        """
        Must return 'No Fraud' with the following inputs
        B=[57.877857,0.311140,1.945940,1,1,0,0]
        """
        B=[57.877857,0.311140,1.945940,1,1,0,0]
        self.assertEqual(Fraud(B),'No Fraud')        
