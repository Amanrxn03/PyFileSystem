import pytest
from pyfilesystem.simulator import VirtualDisk

def test_contiguous_create_and_delete():
    d=VirtualDisk(20,1)
    f=d.create_file("a.txt",3,"contiguous",content="a\nb")
    assert f.blocks == [0,1,2]
    assert d.used_blocks == 3
    assert d.delete_file("/a.txt") == 3
    assert d.free_blocks == 20

def test_linked_and_indexed():
    d=VirtualDisk(20,1)
    a=d.create_file("a",2,"linked")
    b=d.create_file("b",2,"indexed")
    assert len(a.blocks)==2
    assert len(b.blocks)==3

def test_bitmap_persistence_roundtrip():
    from pyfilesystem.simulator import VirtualDisk
    d=VirtualDisk(10,1); d.create_file("x",2,"linked")
    restored=VirtualDisk.from_dict(d.to_dict())
    assert restored.bitmap==d.bitmap

def test_path_traversal_rejected():
    d=VirtualDisk()
    with pytest.raises(ValueError): d.mkdir("x","/../")

def test_permissions():
    d=VirtualDisk()
    d.create_file("secret",1,"contiguous")
    assert d.check_access("/secret","owner","read")
    assert not d.check_access("/secret","others","read")

def test_direct_access_bounds():
    d=VirtualDisk()
    d.create_file("records",1,"contiguous",content="one\ntwo")
    assert d.direct_record("/records",1)=="two"
    with pytest.raises(IndexError): d.direct_record("/records",2)
