import urllib.parse
import sys
from typing import List
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp
from groq import Groq
from config import Settings

# Define extraction schemas for search results
class SearchResult(BaseModel):
    title: str = Field(..., description="Title of search result")
    snippet: str = Field(..., description="Snippet text of search result")
    url: str = Field(..., description="URL of search result")

class ExtractSchema(BaseModel):
    results: List[SearchResult] = Field(..., description="List of top search results")

def main(stock_name: str = None):
    # If stock_name is not provided, prompt the user for input
    if not stock_name:
        # stock_name = input("Enter the stock name (e.g., Asian Paints Ltd): ")
        return Exception("Stock name not provided.")

    # Initialize the FirecrawlApp with your API key
    # print("the api key is: ", Settings.FIRE_CRAWL_API_KEY)
    app = FirecrawlApp(api_key=Settings.FIRE_CRAWL_API_KEY)

    # Build a search query string with factors needed for analysis
    search_query = f"{stock_name} stock analysis profit loss revenue news"
    encoded_query = urllib.parse.quote(search_query)

    # Construct the Bing search URL
    search_url = f"https://www.bing.com/search?q={encoded_query}"

    print("\nScraping search results...")

    # Use Firecrawl to scrape the search results page with our schema
    data = app.scrape_url(search_url, {
        'formats': ['json'],
        'jsonOptions': {
            'schema': ExtractSchema.model_json_schema(),
        }
    })

    # Extract the results from the scraped JSON
    results = data["json"]["results"]

    # Combine the top 5 search results into a single text block for context
    combined_text = ""
    for i, result in enumerate(results[:5], start=1):
        combined_text += (
            f"Result {i}:\n"
            f"Title: {result['title']}\n"
            f"Snippet: {result['snippet']}\n"
            f"URL: {result['url']}\n\n"
        )

    
    return results

# if __name__ == "__main__":
#     # If a stock name is passed as a command-line argument, use it; otherwise, it will be prompted.
#     stock_name_arg = sys.argv[1] if len(sys.argv) > 1 else None
#     main(stock_name_arg)
