"""Basic tests to verify pytest is working."""

import pytest


def test_basic_math():
    """Test basic math operations."""
    assert 2 + 2 == 4
    assert 3 * 3 == 9


def test_string_operations():
    """Test string operations."""
    assert "hello" + " " + "world" == "hello world"
    assert len("test") == 4


def test_list_operations():
    """Test list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15


@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_doubling(input_value, expected):
    """Test parameterized doubling function."""
    assert input_value * 2 == expected


class TestBasicClass:
    """Test class for basic operations."""
    
    def test_instance_method(self):
        """Test instance method."""
        assert True
    
    def test_another_instance_method(self):
        """Test another instance method."""
        assert 1 == 1
