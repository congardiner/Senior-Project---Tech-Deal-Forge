from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def scrape_heading_task(request: Request, data):
    # Visit the Omkar Cloud website
    response = request.get("https://www.omkar.cloud/")

    # Create a BeautifulSoup object    
    soup = soupify(response)
    
    # Retrieve the heading element's text
    heading = soup.find('h1').get_text()

    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        "heading": heading
    }     
# Initiate the web scraping task
scrape_heading_task()