import pytest
from pyfilesystem.validators import validate_name, validate_size, validate_record_position

def test_name():
    assert validate_name("hello.txt")=="hello.txt"
    with pytest.raises(ValueError): validate_name("../bad")
def test_size():
    assert validate_size(4)==4
    with pytest.raises(ValueError): validate_size(-1)
def test_record():
    assert validate_record_position("0",1)==0
    with pytest.raises(IndexError): validate_record_position(1,1)
