from __future__ import annotations

import datetime
import gzip
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field, fields
from typing import IO, Any, Dict, List, Type, TypeVar, Optional, Iterable
from .enums import RecipeStatusEnum, RecipeMealTypeEnum


T = TypeVar("T", bound="PaprikaRecipe")
TNotionRecipe = TypeVar("TNotionRecipe", bound="NotionRecipe")
DEFAULT_DELIM = "\n==========================\n" # Should be moved to some constants file.

@dataclass
class PaprikaRecipe:
    """
    From: `paprika-recipes`: https://github.com/coddingtonbear/paprika-recipes/tree/master

    I wasn't sure exactly how to use this from the installed tool, so I've just re-created it here.
    """
    categories: List[str] = field(default_factory=list)
    cook_time: str = ""
    created: str = field(default_factory=lambda: str(datetime.datetime.utcnow())[0:19])
    description: str = ""
    difficulty: str = ""
    directions: str = ""
    hash: str = field(
        default_factory=lambda: hashlib.sha256(
            str(uuid.uuid4()).encode("utf-8")
        ).hexdigest()
    )
    image_url: str = ""
    ingredients: str = ""
    name: str = ""
    notes: str = ""
    nutritional_info: str = ""
    photo: str = ""
    photo_hash: str = ""
    photo_large: Any = None
    prep_time: str = ""
    rating: int = 0
    servings: str = ""
    source: str = ""
    source_url: str = ""
    total_time: str = ""
    uid: str = field(default_factory=lambda: str(uuid.uuid4()).upper())
    photos: List[Any] = field(default_factory=list)
    photo_data: Optional[str] = None

    @classmethod
    def get_all_fields(cls):
        return fields(cls)

    @classmethod
    def from_file(cls: Type[T], data: IO[bytes]) -> T:
        return cls.from_dict(json.loads(gzip.open(data).read()))

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)

    def as_paprikarecipe(self) -> bytes:
        return gzip.compress(self.as_json().encode("utf-8"))

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self):
        return asdict(self)

    def calculate_hash(self) -> str:
        fields = self.as_dict()
        fields.pop("hash", None)

        return hashlib.sha256(
            json.dumps(fields, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def update_hash(self):
        self.hash = self.calculate_hash()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self}>"



@dataclass
class NotionRecipe:
    recipe: str = ""
    recipe_write_up: str = ""
    meal_type: Optional[RecipeMealTypeEnum] = None
    status: Optional[RecipeStatusEnum] = None
    ingredients: Any = None
    meal_plan: Any = None
    url: str = ""
    tags: List[str] = field(default_factory=list)
    paprika_hash: str = field(default_factory=lambda: hashlib.sha256(
                str(uuid.uuid4()).encode("utf-8")
            ).hexdigest()
        )
    write_up_delim: str = field(default_factory=lambda: DEFAULT_DELIM)

    @classmethod
    def from_paprika(cls: Type[TNotionRecipe], paprika_recipe: PaprikaRecipe) -> TNotionRecipe:
        """TODO: WIP Unfortunately, there's not a great way to go back `to_paprika()`given the way the write_up is constructed.
        Can maybe add some sort of string separator to enable it to be backwards compatible."""
        return cls(
            recipe=paprika_recipe.name,
            recipe_write_up=cls._gen_recipe_write_up_from_paprika(paprika_recipe, DEFAULT_DELIM),
            meal_type=RecipeMealTypeEnum.FROM_PAPRIKA,
            status=RecipeStatusEnum.FROM_PAPRIKA,
            url=paprika_recipe.source_url,
            tags=paprika_recipe.categories,
            paprika_hash=paprika_recipe.hash,

        )

    @staticmethod
    def _gen_recipe_write_up_from_paprika(paprika_recipe, delim: str):
        """TODO: There are many more things that could be included here."""
        directions = paprika_recipe.directions.replace("\n\n", "\n").split("\n")
        out = f"{paprika_recipe.ingredients}{delim}{directions}"
        return out



    def get_title_property(self):
        return {
            "Recipe": {
                "title": [
                    {
                        "text": {
                            "content": self.recipe
                        }
                    }
                ]
            }
        }

    def get_recipe_write_up_property(self):
        return {
            "Recipe write-up": {
                "rich_text": [
                    {
                        "text": {
                            "content": self.recipe_write_up
                        }
                    }
                ]
            }
        }

    def get_meal_type_property(self):
        return {
            "Meal Type": {
                "select": {"name": self.meal_type.value}
            }
        }

    def get_status_property(self):
        return {
            "Status": {
                "select": {"name": self.meal_type.value}
            }
        }

    def get_url_property(self):
        return { 'URL': {'id': 'xOUe', 'type': 'url', 'url': self.url}}

    def get_tags_property(self):
        return {
        "Tags": {'id': 'yzKx',
            'type': 'multi_select',
            'multi_select': [{"name": t for t in self.tags}]}
        }
    def get_all_properties(self):
        properties = {}
        properties.update(self.get_title_property())
        properties.update(self.get_recipe_write_up_property())
        properties.update(self.get_meal_type_property())
        properties.update(self.get_status_property())
        properties.update(self.get_url_property())
        properties.update(self.get_tags_property())
        return {"properties": properties}


    def gen_page_template(self, database_id: str) -> Dict[str, Any]:
        """
        Main entrypoint for generating the page template to POST via Notion API. See each individual function in
        `get_all_properties()` for details on any available kwargs.


        :return:
        """
        page = {}
        page['parent'] = {"database_id": database_id}
        page.update(self.get_all_properties())
        return page

    def gen_ingredient_pages(self):
        """
        Get the first element of the recipe write_up, which contains all the ingredients. Splits these by `\n`.
        Then we need to do something to extract the ingredient token. Some sort of NLTK utility may help here.
        """
        raise NotImplementedError
