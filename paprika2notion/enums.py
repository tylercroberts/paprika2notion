from enum import Enum

# TODO:
# we probably want to reference these by the ID values rather than strings..
# Can probably scrape this from the API by `retreiving` the database.
# Unsure if we can create an Enum based on this programmatically, but maybe some other class
########## Yes you can:
# https://stackoverflow.com/questions/33690064/dynamically-create-an-enum-with-custom-values-in-python
# That would take in a string, and return the ID if lower, else just returns {"name": input_string}


# For the time being, these things will all take the value: FROM_PAPRIKA, in order to make it easy to detect which Recipes
# need to be actioned/updated.


##################################
# Ingredients
##################################
class IngredientStatusEnum(Enum):
    OUT_OF_STOCK = "Out of Stock"
    SHOPPING_LIST = "Shopping List"
    IN_STOCK = "In Stock"


class IngredientTypeEnum(Enum):
    pass

class IngredientStoreEnum(Enum):
    pass


##################################
# Recipes
##################################
class RecipeStatusEnum(Enum):
    WISHLIST = "Wishlist"
    WIP = "WIP"
    TRIED_AND_TESTED = "Tried and tested"
    FROM_PAPRIKA = "From Paprika"


class RecipeMealTypeEnum(Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"
    BEVERAGE = "Beverage"
    BRUNCH = "Brunch"
    SMOOTHIE = "Smoothie"
    MISC = "Misc"
    FROM_PAPRIKA = "From Paprika"

##################################
# Meal Plans
##################################