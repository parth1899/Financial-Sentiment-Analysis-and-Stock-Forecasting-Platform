from flask import Flask, request, jsonify
from flask_cors import CORS
from helper.query_processing import QueryProcessor
from api_endpoints.stock_api import fetch_stock
from api_endpoints.news_api import fetch_news
from api_endpoints.twitter_api import fetch_twitter
from sentiment_analysis.sentiment import analyze_sentiment
from concurrent.futures import ThreadPoolExecutor, as_completed
from helper.citations import main

app = Flask(__name__)
CORS(app)

# Global variable to hold the extracted query components.
extracted = None
user_query = None
news_analysis = None # global variable to pass news data to sentiment analysis

@app.route('/query', methods=['POST'])
def process_query():
    global extracted
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query not provided"}), 400

    global user_query
    user_query = data['query']
    print(f"Received query: {user_query}")

    # Process the query to extract components.
    query_processor = QueryProcessor()
    extracted = query_processor.process_query(user_query)
    print(f"Extracted components: {extracted}")

    print(f"Extracted news tag: {extracted.news}")

    # Store the extracted components in a global variable.
    # global extracted
    # extracted = extracted

    return jsonify({"result": extracted.dict()})

@app.route('/query_concurrent', methods=['GET'])
def process_query_concurrent():
    # Ensure that the global_extracted has been set.
    global extracted
    if not extracted:
        return jsonify({"error": "No extracted data found. Please call /query first."}), 400
    
    print(f"Extracted components: {extracted}")

    # Call the three helper functions concurrently using the global extracted components.
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_component = {
            executor.submit(fetch_news, extracted.news): "news",
            # executor.submit(fetch_stock, extracted.stock): "stock",
            # executor.submit(fetch_twitter, extracted.twitter): "twitter"
        }
        results = {}
        for future in as_completed(future_to_component):
            component = future_to_component[future]
            try:
                results[component] = future.result()
            except Exception as exc:
                results[component] = {"error": str(exc)}

    global news_analysis
    # Extract content from the first article
    news_articles = results.get("news", {}).get("articles", [])
    if news_articles and "content" in news_articles[0]:
        news_analysis = news_articles[0]["content"]
    else:
        news_analysis = "No relevant news content available."

    print(f"Stored news_analysis: {news_analysis}")

    return jsonify({"result": results})

@app.route('/sentiment', methods=['GET'])
def get_sentiment():
    global news_analysis
    print(f"News analysis: {news_analysis}")
    sentiment_result = analyze_sentiment(news_analysis)

    for item in sentiment_result:
        print(f"Label: {item['label']} | Score: {item['score']:.4f}")

    return jsonify({"result": sentiment_result})


@app.route('/validations', methods=['GET'])
def get_validations():
    global extracted
    print(f"Stock name: {extracted.stock}")
    citations = main(extracted.stock)
    return jsonify({"result": citations})

@app.route('/graphs', methods=['GET'])
def get_graphs():
    global extracted
    print(f"Stock name: {extracted.stock}")
    return jsonify({"result": "Graphs will be displayed here."})


@app.route('/recommendation', methods=['GET'])
def get_recommendation():
    global user_query
    print(f"User query: {user_query}")
    return jsonify({"result": "Recommendation will be displayed here."})

if __name__ == '__main__':
    app.run(debug=True)
