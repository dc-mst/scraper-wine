from bs4 import BeautifulSoup, NavigableString, Tag
from csv_writer import save_to_csv
from selenium_config import setup_vivino

def extract_with_spaces(element):
    texts = [child.get_text(separator=" ").strip() for child in element.children if isinstance(child, (NavigableString, Tag))]
    return ' '.join(texts).strip()

def scrape_vivino():
    # URL of the wine list page
    url = 'https://www.vivino.com/explore?e=eJwNyjEOgzAQBMDfbO0UlKtU4QFIVCiKzPlAp2CDbCfCv4ep5ymN_QBpZXrTKoSvccC68O-zafUbYuYD-9w4a6mfw-RbsOfAoEUQ_cnOOURLdDju-UtBF0saqOkC3togAQ'

    # Initialize the browser using the setup_browser function from the selenium_config module
    browser = setup_vivino(url)

    # Get the page source using Selenium
    page_source = browser.page_source

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract wine
    wine_cards = soup.select('div[data-testid="wineCard"]')

    results = []

    for wine in wine_cards:
        a_element = wine.select_one('a[data-testid="vintagePageLink"]')
        href_value = a_element['href']
        
        # Navigate to the wines URL to get the detailed description
        browser.get("https://www.vivino.com/FR/en" + href_value)
        detail_soup = BeautifulSoup(browser.page_source, 'html.parser')
        
        # Extract desired elements
        winery = detail_soup.select_one("h1 span.headline").get_text().strip() if detail_soup.select_one("h1 span.headline") else ""
        name = detail_soup.select_one("h1 span.vintage").get_text().strip() if detail_soup.select_one("h1 span.vintage") else ""
        region = detail_soup.select_one('a[data-cy="breadcrumb-region"]').get_text().strip() if detail_soup.select_one('a[data-cy="breadcrumb-region"]') else ""

        # Store extracted data into the results list
        results.append({
            "winery": winery,
            "name": name,
            "region": region
        })

    # Save results to CSV
    save_to_csv(results)

    # Close the Selenium browser
    browser.quit()

    return results
