import requests

ES_ENDPOINT = 'http://localhost:5050/recipes'

TARGETS = {
    "Brown sugar & cinnamon glazed popcorn": [
        {"q": "cinnamon popcorn", "filters": {}},
        {"q": "cinnamon", "filters": {}},
        {"q": "cinnamon", "filters": {"gluten_free": "true"}},
        {"q": "sugar butter kernel", "filters": {}}
    ],
    "Spinach savoury muffins": [
        {"q": "spinach muffins", "filters": {}},
        {"q": "muffins", "filters": {"vegetarian": "true"}},
        {"q": "vegetable muffins", "filters": {}}
    ],
    "Vegan waffles with maple & soy mushrooms": [
        {"q": "waffles", "filters": {}},
        {"q": "waffle", "filters": {"vegan": "true"}},
        {"q": "mushroom waffles", "filters": {}}
    ],
    "Barbecue beef burger": [
        {"q": "burger", "filters": {}},
        {"q": "beef burger", "filters": {}},
        {"q": "barbecue burger", "filters": {}}
    ],
    "Chinese chicken curry": [
        {"q": "chicken curry", "filters": {}},
        {"q": "chinese curry", "filters": {}},
        {"q": "spicy chicken", "filters": {}}
    ]
}


def find_rank(target_title, query_text, filters):
    params = {'q': query_text}
    params.update(filters)

    try:
        response = requests.get(ES_ENDPOINT, params=params)
        results = response.json()

        for i, recipe in enumerate(results):
            if recipe['title'] == target_title:
                return i + 1
        return ">10"
    except Exception:
        return "Error"


def main():
    print(f"{'TARGET RECIPE':<30} | {'QUERY + FILTERS':<40} | {'RANK'}")
    print("-" * 80)

    for target, scenarios in TARGETS.items():
        print(f"{target}")
        for case in scenarios:
            q = case['q']
            fil = case['filters']

            filter_str = f" + [{list(fil.keys())[0]}]" if fil else ""
            display_query = f"'{q}'{filter_str}"

            rank = find_rank(target, q, fil)

            print(f"{'':<30} | {display_query:<40} | {str(rank)}")
        print("-" * 80)


if __name__ == "__main__":
    main()
