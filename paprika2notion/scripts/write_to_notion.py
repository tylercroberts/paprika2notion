from paprika2notion import PaprikaRecipe, NotionRecipe
from notion_client import Client
from notion_client.errors import APIResponseError
from loguru import logger
from pathlib import Path
import glob
import argparse
import yaml
import os

logger.add("debug.log")
logger.add("info.log", level="INFO")
logger.add("warning.log", level="WARNING")

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of the extracted archive directory. Should end with `/`")

if __name__ == '__main__':
    failed_recipes = []
    args = parser.parse_args()
    dir_path = Path(args.path)
    c = Client(auth=os.environ["NOTION_TOKEN"])
    archive_glob = glob.glob(str(dir_path / "*.yaml"))
    logger.info(f"Initialized with path: {dir_path}!")
    logger.info(f"Found the {len(archive_glob)} archive files")
    for fn in archive_glob:
        logger.debug(f"Attempting to open: {fn}")
        n = None
        try:
            with open(fn, 'r', encoding='utf8') as f:
                t = PaprikaRecipe.from_dict(yaml.load(f, Loader=yaml.loader.Loader))
            n = NotionRecipe.from_paprika(t)

        except Exception as e:
            logger.error(f"Unable to read: {fn} - {e}")
            raise e

        try: # Writing loop
            n.write_to_notion(c, os.environ["NOTION_RECIPE_DB_ID"])
            logger.debug(f"Successfully wrote {n.recipe} with hash {n.paprika_hash} to Notion")
        except APIResponseError as e: # So the error is not in reading, but in writing
            logger.warning(f"Failed to write {n.paprika_hash} - {e} - {e.body}")
            failed_recipes.append(fn)
            raise
        except Exception as e:
            # TODO This error handling needs to be more specific, so we can export the paprika hashes to logfiles
            logger.warning(f"failed for some other reason {fn} - {e}")

    logger.warning(f"The following Recipes failed to be written: {failed_recipes}")