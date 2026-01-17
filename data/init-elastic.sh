#!/bin/sh

apk update
apk add curl jq

echo "Waiting for Elasticsearch..."
until curl -s http://elasticsearch:9200 >/dev/null; do
  sleep 2
done

echo "Elasticsearch is up."

curl -s -X DELETE "http://elasticsearch:9200/recipes" >/dev/null
echo "Old index deleted (if existed)."

curl -s -X PUT "http://elasticsearch:9200/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "number_of_shards": 1,
      "analysis": {
        "filter": {
          "my_synonym_filter": {
            "type": "synonym_graph",
            "synonyms_path": "synonyms.txt"
          }
        },
        "analyzer": {
          "my_search_analyzer": {
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "my_synonym_filter"
            ]
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "title": {
          "type": "text",
          "search_analyzer": "my_search_analyzer"
        },
        "vegetarian": { "type": "boolean" },
        "vegan": { "type": "boolean" },
        "keto": { "type": "boolean" },
        "dairy_free": { "type": "boolean" },
        "gluten_free": { "type": "boolean" },
        "egg_free": { "type": "boolean" },
        "nut_free": { "type": "boolean" },
        "ingredients": {
          "type": "nested",
          "properties": {
            "quantity": { "type": "keyword" },
            "unit": { "type": "keyword" },
            "ingredient": {
              "type": "text",
              "search_analyzer": "my_search_analyzer"
            },
            "note": { "type": "text" }
          }
        }
      }
    }
  }'
echo "Index created."

jq -c '.[] | {index: { _index: "recipes" }}, .' /recipes_parsed.json | \
  curl -s -X POST "http://elasticsearch:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @-

echo "Recipes loaded!"
