"""
Sample test for our project
"""

from django.test import SimpleTestCase
from . import calc


class calcTests(SimpleTestCase):
    """
    Test the calc module
    """
    def test_add_numbers(self):
        """
        Testing the add_numbers module
        """
        res = calc.add_numbers(1, 2)
        self.assertEqual(res, 3)
