# Setup
Run `pip install paprika2notion`

V0 of this library will assume you have downloaded and extracted your recipes to some path that we will refer to as: `path/to/your/extracted/recipe.paprikarecipe.yaml`

For help doing this, check out: [paprika-recipes](https://github.com/coddingtonbear/paprika-recipes)

You must then create a Notion database that provides write-access to a Notion integration. For details on setting up a Notion integration, see their website [here](https://www.notion.so/help/create-integrations-with-the-notion-api#create-an-internal-integration)

This database must contain, at minimum the following fields. Note that spelling matters, as the names are used for writing the template.:
- Title: `Recipe`
- Rich Text: `Recipe write-up`, `Paprika Hash`
- Select: `Status`, `Meal Type`, `Tags`
- URL: `URL`


If you wish for a different field-set, you can edit the NotionRecipe's `get_all_properties` method.

The library reads your secrets from environment variables. **See the snippet below for expected variables.**
I recommend using a secrets manager like Hashicorp Vault (not sponsored) to enable this. 
Otherwise, you can create a local config file.


# Usage

This library is intended to make it easy for you to load recipes you have stored in [Paprika](https://www.paprikaapp.com/) into your Notion Workspace.


Once you have downloaded and extracted your recipes, you can load them as objects in python, edit them, and write to notion if you wish. 

See below for an example writing a single recipe to my Notion database.

```python

#%%
from __future__ import annotations
import os
import yaml
from paprika2notion import PaprikaRecipe, NotionRecipe
from notion_client import Client

c = Client(auth=os.environ["NOTION_TOKEN"])

with open("path/to/your/extracted/recipe.paprikarecipe.yaml", 'r', encoding='utf8') as f:
    t = PaprikaRecipe.from_dict(yaml.load(f, Loader=yaml.loader.Loader))

n = NotionRecipe.from_paprika(t)
n.write_to_notion(c, os.environ["NOTION_DATABASE_ID"])

```

By default, the tool will do a few things:
- All categories in Paprika become `Tags` in Notion
- `Status` and `Meal Type` are set to `From Paprika`, to enable you to identify recipes that may need touching up in Notion.
- Paprika's `Directions` are written to `Recipe write-up`, and if > 2000 characters, overflow goes to `Recipe write-up overflow`


# Contribution

There are a number of ways to contribute to paprika2notion.

- Check out open Issues and submit a PR to resolve one
  - if you don't want to submit a PR, feel free to join the discussion on these issues anyways!
- Use the tool and make improvements to solve your pain points
  - Find something annoying? We'd love your help fixing it! Anything that could make this a more seamless tool is probably welcome.
  - 

- Some planned items that you're free to take a stab at before I get to them:
  - Automatically create appropriate Database/Page/Schema in Notion from tool
  - Automatically add all ingredient relations
    - If ingredient doesn't exist, create an appropriate one
  
- Just ask! Feel free to reach out to me and ask if there's anything you can do to help with the project. Almost certainly we have some backlog items.


With any pull request, please include at minimum:
- Doc strings for any major functions/methods.
- a test case walkthrough.

If you're feeling especially helpful create a test using pytest and run it with `cov` after your changes.
