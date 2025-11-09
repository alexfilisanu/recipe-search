import json
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_recipes_df():
    def get_urls():
        urls_df = pd.DataFrame(columns=['recipe_urls'])
        page = 1
        while True:
            url = f'https://www.bbcgoodfood.com/recipes/page/{page}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            html = requests.get(url, headers=headers)

            # Stop if page not found
            if html.status_code != 200:
                break

            soup = BeautifulSoup(html.text, 'html.parser')
            recipe_urls = [
                a.get("href") for a in soup.find_all("a")
                if "/recipes/" in a.get("href", "")
                   and "-" in a.get("href", "")
                   and "category" not in a.get("href", "")
                   and "collection" not in a.get("href", "")
            ]

            # Remove duplicates
            recipe_urls = list(set(recipe_urls))
            df = pd.DataFrame({"recipe_urls": recipe_urls})
            urls_df = pd.concat([urls_df, df], ignore_index=True)

            page += 1

        urls_df['recipe_urls'] = urls_df['recipe_urls'].apply(lambda x: f"https://www.bbcgoodfood.com{x}" if x.startswith("/") else x)
        list_urls = urls_df['recipe_urls'].to_list()
        recipes_df = pd.DataFrame(columns=[
            'title', 'vegetarian', 'vegan', 'dairy_free', 'keto', 'gluten_free', 'egg_free', 'nut_free',
            'prep_time', 'cook_time', 'ingredients', 'nutrition'
        ])
        return list_urls, recipes_df

    def get_recipes(list_urls):
        new_rows = []
        headers = {'User-Agent': 'Mozilla/5.0'}

        for url in list_urls:
            html = requests.get(url, headers=headers, allow_redirects=False)
            soup = BeautifulSoup(html.text, 'html.parser')

            recipe_title = soup.find('h1', {'class': 'heading-1'}).text \
                if soup.find('h1', {'class': 'heading-1'}) else "N.A."

            prep_time = cook_time = "N.A."
            time_blocks = soup.select(
                "div.recipe-cook-and-prep-details__section div.recipe-cook-and-prep-details__item")
            for block in time_blocks:
                text = block.get_text(" ", strip=True)
                if "Prep" in text:
                    prep_time = text.replace("Prep:", "").strip()
                elif "Cook" in text:
                    cook_time = text.replace("Cook:", "").strip()

            tags = [t.get_text(strip=True).lower() for t in soup.select("div.post-header--masthead__tags-item")]
            vegetarian = "vegetarian" in tags
            vegan = "vegan" in tags
            keto = "keto" in tags
            dairy_free = "dairy-free" in tags
            gluten_free = "gluten-free" in tags
            egg_free = "egg-free" in tags
            nut_free = "nut-free" in tags

            ingredients_section = soup.find('ul', {'class': 'ingredients-list list'})
            ingredient_list = [
                ingredient.get_text(separator=' ', strip=True) for ingredient in
                ingredients_section.find_all('li', class_='ingredients-list__item')
            ] if ingredients_section else []

            # Skip recipes with no ingredients(advertisements)
            if not ingredient_list:
                continue

            nutrition_section = soup.find('ul', {'class': 'nutrition-list'})
            nutrition_list = [
                nutrition.get_text(separator=' ', strip=True) for nutrition in
                nutrition_section.find_all('li', class_='nutrition-list__item')
            ] if nutrition_section else []

            new_row = {
                'title': recipe_title, 'vegetarian': vegetarian, 'vegan': vegan, 'keto': keto,
                'dairy_free': dairy_free, 'gluten_free': gluten_free, 'egg_free': egg_free, 'nut_free': nut_free,
                'prep_time': prep_time, 'cook_time': cook_time, 'ingredients': ingredient_list,
                'nutrition': nutrition_list
            }
            new_rows.append(new_row)
            print(f"Extracted recipe: {recipe_title}")

        recipes_df = pd.DataFrame(new_rows)
        return recipes_df

    list_urls, recipes_df = get_urls()
    recipes_df = get_recipes(list_urls)
    return recipes_df


if __name__ == '__main__':
    recipes_df = get_recipes_df()
    recipes_list = recipes_df.to_dict(orient='records')

    with open(f'bbc_good_food_recipes.json', 'w') as json_file:
        json.dump(recipes_list, json_file, indent=4)
