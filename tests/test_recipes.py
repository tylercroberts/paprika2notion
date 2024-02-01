import time
import pytest
from paprika2notion import PaprikaRecipe, NotionRecipe
from paprika2notion.recipe import sleep_util
from loguru import logger
from pathlib import Path
logger.add('test_logs.log')


# Will need tot create a fixture to load the PaprikaRecipe based on one of my current ones.

@pytest.fixture
def paprika_recipe_filepath():
    return Path(__file__).parent.joinpath("fixtures/example.paprikarecipe.yaml")
@pytest.fixture
def paprika_recipe(paprika_recipe_filepath):
    return PaprikaRecipe.from_yaml(paprika_recipe_filepath)

@pytest.fixture
def notion_recipe(paprika_recipe):
    return NotionRecipe.from_paprika(paprika_recipe)


def test_paprika(paprika_recipe_filepath):
    recipe = PaprikaRecipe.from_yaml(paprika_recipe_filepath)
    assert isinstance(recipe.ingredients, str)
    zipped = recipe.as_paprikarecipe()
    recipe.get_all_fields()
    recipe.calculate_hash()
    recipe.update_hash()
    print(recipe)

    # This needs to be last to test the __repr__ method
    recipe


def test_notion(paprika_recipe):
    # TODO: Figure out how to give this unit test access to Vault or something.
    # I guess if I run vlt pytest
    recipe = NotionRecipe.from_paprika(paprika_recipe)
    print(recipe)
    api_body = recipe.gen_page_template("test_db_id")
    assert api_body['database_id'] == "test_db_id"
    assert isinstance(api_body['properties'], dict)
    # This needs to be last to test the __repr__ method
    recipe


def test_utils():
    sleep_util(1)
    with pytest.raises(TypeError):
        sleep_util("banana")