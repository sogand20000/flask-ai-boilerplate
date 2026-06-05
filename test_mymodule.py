# استایل مدرن pytest (بدون نیاز به ساخت کلاس و ارث‌بری)
from backend.src.mymodule import doubler, square


def test_square():
    assert square(2) == 8


def test_doubler():
    assert doubler(2) == 4
