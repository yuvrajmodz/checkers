from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import os

app = Flask(__name__)

def check_domain_status(domain):
    with sync_playwright() as p:
        # Open browser and go to NordVPN link checker
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://nordvpn.com/link-checker")

        # Wait for the input field and fill it with the domain
        page.fill('input[data-hk="s10-0-0-1-1-0"]', domain)

        # Click on the analyze button
        page.click('button[data-hk="s10-0-0-1-3-0-0"]')

        # Wait for 4 seconds to allow the result to load
        time.sleep(4)

        # Scrape the result page using BeautifulSoup
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Find the result paragraph and extract the domain status
        result = soup.find('p', class_='body-md')
        if result:
            domain_status = result.text.strip()
        else:
            domain_status = "Could not determine domain status."

        # Close browser
        browser.close()

    return domain_status

@app.route('/check=<domain>', methods=['GET'])
def check_domain(domain):
    # Perform domain status check
    domain_status = check_domain_status(domain)

    # Return the result in JSON format
    return jsonify({
        domain: domain_status
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5012))
    app.run(host='0.0.0.0', port=port, debug=True)
