"این ماژول تست واحد برای mymoduleانجام می دهد"

import unittest
from mymodule import square, doubler


class TestMyModule(unittest.TestCase):
    "کلاس تست برای توابع ریاضی"

    def test_square(self):
        "تست کردن صحت عملکرد تابع جذر یا مربع"
        self.assertEqual(square(2), 4, "برای ورودی 2 درست نیست حطا square")

    def test_doubler(self):
        "تست کردن صحت عملکرد تابغ دوبرابر کننده"
        self.assertEqual(doubler(3), 6)


if __name__ == "__main__":
    unittest.main()
