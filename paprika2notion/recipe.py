from __future__ import annotations

import time
import datetime
import gzip
import hashlib
import json
from loguru import logger
import uuid
from dataclasses import asdict, dataclass, field, fields
from typing import IO, Any, Dict, List, Type, TypeVar, Optional, Iterable
from .enums import RecipeStatusEnum, RecipeMealTypeEnum


T = TypeVar("T", bound="PaprikaRecipe")
TNotionRecipe = TypeVar("TNotionRecipe", bound="NotionRecipe")
DEFAULT_DELIM = "\n==========================\n" # Should be moved to some constants file.

def sleep_util(sleep_time: int=30):
    logger.debug(f"Sleeping {sleep_time}s to avoid rate-limit")
    time.sleep(sleep_time)


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
        # Will this be consistent w/ the UID below if none are provided at all? Also, it doesn't use upper like the actual UUID file)
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

    @classmethod
    def from_notion_api(cls: Type[TNotionRecipe], notion_api_item: Dict[str, Any]) -> TNotionRecipe:
        raise NotImplementedError

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
        page = dict()
        page['parent'] = {"database_id": database_id}
        page.update(self.get_all_properties())
        return page

    def gen_ingredient_pages(self):
        """
        Get the first element of the recipe write_up, which contains all the ingredients. Splits these by `\n`.
        Then we need to do something to extract the ingredient token. Some sort of NLTK utility may help here.
        """
        raise NotImplementedError

    def write_to_notion(self, notion_client, database_id):
        all_notion_rows = self.get_all_notion_rows(notion_client, database_id, self.paprika_hash)
        # TODO: If this just returns NotionRecipe items, it would be easier to do this check.
        matching_notion_row = [
            row for row in all_notion_rows
            if row['properties']['Paprika Hash']['rich_text'][0]['text']['content'] == self.paprika_hash
        ]

        n_matches = len(matching_notion_row)
        assert n_matches < 2, "Duplicates are present in the notion database"

        if n_matches == 1:
            logger.info(f"Notion already contains data for: {self.recipe} - {self.paprika_hash}")

            #TODO: Add some sort of last update concept
            # For now, we just


            # mendeleyTime = it.last_modified.to('US/Pacific')
            # notionTime = arrow.get(notionRow['last_edited_time']).to('US/Pacific')

            # last modified time on Mendeley is AFTER last edited time on Notion
            # if mendeleyTime > notionTime:
            #     logger.debug(f'Updating row {notionRow["id"]} in notion')
            #     pageID = notionRow['id']
            #     propObj = getPropertiesForMendeleyDoc(it, localPrefix=mendeley_filepath)
            #     notionPage = getNotionPageEntryFromPropObj(propObj)
            #     try:
            #         notion.pages.update(pageID, properties=notionPage)
            #     except:
            #         sleep_util(30)
            #         notion.pages.update(pageID, properties=notionPage)

            # else:  # Nothing to update
            #     pass

        elif n_matches == 0:
            logger.debug(f'No results matched query for {self.recipe} - {self.paprika_hash}. Creating new row')
            # extract properties and format it well
            notion_page = self.gen_page_template(database_id)
            try:
                notion_client.pages.create(parent={"database_id": database_id}, properties=notion_page)
            except:  # TODO: See note in `get_all_notion_rows()` about this sleeping on _any_ error.
                sleep_util(30)
                notion_client.pages.create(parent={"database_id": database_id}, properties=notion_page)

        else:
            raise NotImplementedError

    @classmethod
    def get_all_notion_rows(cls: Type[TNotionRecipe], notion_client,
                            database_id: str, recipe_hash: str=None) -> List[TNotionRecipe]:
        """
        Gets all rows (pages) from a notion database using a notion client
        # TODO: Currently if there are _any_ errors, it waits 30s before failing.
        # TODO: Could make the try-excepts a bit more specific to enable fast-failing

        Args:
            notion_client: (notion Client) Notion client object
            database_id: (str) string code id for the relevant database
            recipe_hash: (str) string hash for a given recipe. If provided, will only query for that ID
        Returns:
            all_notion_rows: (list of notion rows)
            # TODO: convert to NotionRecipe objects

        """
        start = time.time()
        has_more = True
        all_notion_rows = list()
        i = 0
        request_payload = {"database_id": database_id}
        next_cursor = None

        if recipe_hash is not None:
            request_payload.update({"filter": {"property": "Paprika Hash", "text": {"equals": recipe_hash}}})

        # Will try to get _all_ rows if no
        while has_more:
            if i == 0:
                try:
                    query = notion_client.databases.query(
                        **request_payload
                    )
                except:
                    sleep_util(30)
                    query = notion_client.databases.query(
                        **request_payload
                    )

            else:
                request_payload.update({"start_cursor": next_cursor})
                try:
                    query = notion_client.databases.query(
                        **request_payload
                    )
                except:
                    sleep_util(30)
                    query = notion_client.databases.query(
                        **request_payload
                    )

            all_notion_rows.extend(query['results'])
            next_cursor = query['next_cursor']
            has_more = query['has_more']
            i += 1

        end = time.time()
        logger.info('Number of rows in notion currently: ' + str(len(all_notion_rows)))
        logger.info('Total time taken: ' + str(end - start))

        return all_notion_rows
