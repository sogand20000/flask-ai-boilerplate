from src.myproject.module1 import doubler, square


def test_my_package_functions():
    assert square(4) == 16
    assert doubler(4) == 8
