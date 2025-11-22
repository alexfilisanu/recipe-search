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
    title = request.args.get("title")
    if title:
        query = {
            "query": {
                "match": {
                    "title": {
                        "query": title,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
    else:
        query = {"query": {"match_all": {}}}

    res = es.search(index=INDEX, query=query["query"], size=20)
    recipes = [hit["_source"] for hit in res["hits"]["hits"]]
    return jsonify(recipes)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
