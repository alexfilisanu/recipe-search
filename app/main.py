from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch("http://elasticsearch:9200")

INDEX = "recipes"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes", methods=["GET"])
def get_recipes():
    query = request.args.get("q", "").strip()
    filters = []
    dietary_fields = ["vegetarian", "vegan", "keto", "dairy_free", "gluten_free", "egg_free", "nut_free"]

    for field in dietary_fields:
        if request.args.get(field) == "true":
            filters.append({"term": {field: True}})

    if query:
        search_query = {
            "bool": {
                "filter": filters,
                "must": [
                    {
                        "bool": {
                            "should": [
                                # 1. EXACT PHRASE MATCH (x10 boost)
                                {
                                    "match_phrase": {
                                        "title": {
                                            "query": query,
                                            "boost": 10
                                        }
                                    }
                                },
                                # 2. FULL TITLE MATCH (x5 boost)
                                {
                                    "match": {
                                        "title": {
                                            "query": query,
                                            "boost": 5,
                                            "fuzziness": "AUTO",
                                            "operator": "and"
                                        }
                                    }
                                },
                                # 3. PARTIAL TITLE MATCH (x2 boost)
                                {
                                    "match": {
                                        "title": {
                                            "query": query,
                                            "boost": 2,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                },
                                # 4. INGREDIENTS MATCH (x1 boost - sum scores of all ingredients)
                                {
                                    "nested": {
                                        "path": "ingredients",
                                        "query": {
                                            "match": {
                                                "ingredients.ingredient": {
                                                    "query": query,
                                                    "boost": 1,
                                                    "fuzziness": "AUTO"
                                                }
                                            }
                                        },
                                        "score_mode": "sum"
                                    }
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ]
            }
        }
    else:
        search_query = {
            "bool": {
                "filter": filters,
                "must": {"match_all": {}}
            }
        }

    res = es.search(
        index=INDEX,
        query=search_query,
        highlight={"fields": {"title": {}, "ingredients.ingredient": {}}},
        size=10
    )

    recipes = []
    for hit in res["hits"]["hits"]:
        data = hit["_source"]
        data["_highlight"] = hit.get("highlight", {})
        recipes.append(data)

    return jsonify(recipes)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
