import pytest
from render_engine.collection import Collection
from render_engine.page import Page
from pathlib import Path

def test_collections_discovers_title(base_collection, custom_collection):
    assert base_collection.title == "MyCollection"
    assert custom_collection.title == "My Custom Title"

def test_collections_accept_custom_vars(custom_collection):
    assert custom_collection.foo == "bar"

def test_collection_passes_vars_to_page(base_collection, temp_dir_collection):
    assert base_collection.pages[Path(temp_dir_collection/'fake_path_0.md')].collection_title == "MyCollection"

def test_collection_pages_are_content_type(temp_dir_collection):
    class CustomPage(Page):
        pass

    class MyCollection(Collection):
        content_type = CustomPage
        content_path = temp_dir_collection
    assert isinstance(MyCollection().pages[Path(temp_dir_collection/'fake_path_0.md')], CustomPage)
    
def test_collection_inherits_custom_attrs_from_init():
    assert Collection(foo="bar").foo == "bar"


def test_collection_with_bad_path_raises_error():
    class BadPathCollection(Collection):
        content_path = Path('bad_path')

    with pytest.raises(ValueError) as e:
        BadPathCollection().pages()


def test_collection_render_archives_loaded(temp_dir_collection, base_collection):
    base_collection.render_archives(path=temp_dir_collection)
    archive = temp_dir_collection.joinpath('mycollection.html')
    assert archive.exists()
    assert archive.read_text() == "Foo"