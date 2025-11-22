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
    query = request.args.get("q")
    filters = []

    # dietary filters (checkboxes in frontend)
    for field in ["vegetarian", "vegan", "keto", "dairy_free", "gluten_free", "egg_free", "nut_free"]:
        value = request.args.get(field)
        if value == "true":
            filters.append({"term": {field: True}})

    must_queries = []

    if query:
        terms = query.split()

        must_queries.append({
            "bool": {
                "should": [
                    # highest priority: TITLE matches ALL words (x5)
                    {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "title": {
                                            "query": term,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                } for term in terms
                            ],
                            "boost": 5
                        }
                    },
                    # 2nd priority: TITLE matches ANY word (x2)
                    {
                        "bool": {
                            "should": [
                                {
                                    "match": {
                                        "title": {
                                            "query": term,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                } for term in terms
                            ],
                            "boost": 2
                        }
                    },
                    # 3rd priority: INGREDIENTS matches ALL words (x3)
                    {
                        "nested": {
                            "path": "ingredients",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "match": {
                                                "ingredients.ingredient": {
                                                    "query": term,
                                                    "fuzziness": "AUTO"
                                                }
                                            }
                                        } for term in terms
                                    ]
                                }
                            },
                            "boost": 3
                        }
                    },
                    # 4th priority: INGREDIENTS matches ANY word (x1)
                    {
                        "nested": {
                            "path": "ingredients",
                            "query": {
                                "bool": {
                                    "should": [
                                        {
                                            "match": {
                                                "ingredients.ingredient": {
                                                    "query": term,
                                                    "fuzziness": "AUTO"
                                                }
                                            }
                                        } for term in terms
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        })

    res = es.search(
        index=INDEX,
        query={"bool": {"must": must_queries + filters}} if must_queries or filters else {"match_all": {}},
        highlight={"fields": {"title": {}, "ingredients.ingredient": {}}},
        size=10
    )

    recipes = []
    for hit in res["hits"]["hits"]:
        data = hit["_source"]
        data["_highlight"] = hit.get("highlight", {})
        recipes.append(data)

    print(jsonify(recipes))
    return jsonify(recipes)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
