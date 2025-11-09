import json
import spacy
from ingredient_parser import parse_ingredient


nlp = spacy.load("en_core_web_sm")


def singularize_ingredient(ingredient):
    doc = nlp(ingredient)
    lemmas = [token.lemma_ for token in doc if token.pos_ in ("NOUN", "PROPN")]
    if lemmas:
        return " ".join(lemmas)
    return ingredient


def serialize_fraction(f):
    if f is None:
        return None
    return str(f)


def get_quantity_unit(parsed):
    if not parsed.amount:
        return None, None

    quantities = []
    units = []

    for amt in parsed.amount:
        # CompositeIngredientAmount
        if hasattr(amt, "amounts"):
            for a in amt.amounts:
                quantities.append(serialize_fraction(a.quantity))
                units.append(str(a.unit))
        else:
            quantities.append(serialize_fraction(amt.quantity))
            units.append(str(amt.unit))

    return quantities, units


def parse_recipe_ingredients(recipes):
    parsed_recipes = []

    for recipe in recipes:
        parsed_ingredients = []
        for ingredient_text in recipe.get("ingredients", []):
            parsed = parse_ingredient(ingredient_text)
            quantity, unit = get_quantity_unit(parsed)
            ingredient_raw = parsed.name[0].text if parsed.name else None
            ingredient = singularize_ingredient(ingredient_raw) if ingredient_raw else None
            note = parsed.preparation.text if parsed.preparation else parsed.comment.text if parsed.comment else None

            parsed_ingredients.append({
                "quantity": quantity[0] if quantity else None,
                "unit": unit[0] if unit else None,
                "ingredient": ingredient,
                "note": note
            })

        new_recipe = recipe.copy()
        new_recipe["ingredients"] = parsed_ingredients
        parsed_recipes.append(new_recipe)

    return parsed_recipes


if __name__ == '__main__':
    with open("bbc_good_food_recipes.json", "r") as f:
        recipes = json.load(f)

    parsed_recipes = parse_recipe_ingredients(recipes)

    with open("recipes_parsed.json", "w") as f:
        json.dump(parsed_recipes, f, indent=4)
