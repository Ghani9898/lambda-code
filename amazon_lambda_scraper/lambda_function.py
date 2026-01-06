import time
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

S3_BUCKET = "testing-lambda-code-123"
S3_KEY = "index.html"


def lambda_handler(event, context):
    url = event.get(
        "url",
        "https://www.amazon.com/s?k=laptop&crid=17ADEKT6RYTQN&sprefix=laptop%2Caps%2C363&ref=nb_sb_noss_1"
    )

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--single-process")

    # ✅ CORRECT paths for your uploaded layer
    chrome_options.binary_location = "/opt/headless-chromium"
    service = Service("/opt/chromedriver")

    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(3)

        # Scroll to load products
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract products
        elements = driver.find_elements(By.CLASS_NAME, "puisg-col")
        products = [elem.text for elem in elements if elem.text.strip()]

    finally:
        if driver:
            driver.quit()

    # Build HTML
    html_content = """
    <html>
      <head><title>Amazon Products</title></head>
      <body>
        <h1>Amazon Laptop Results</h1>
        <ul>
    """

    for product in products:
        html_content += f"<li>{product.replace(chr(10), '<br>')}</li>"

    html_content += """
        </ul>
      </body>
    </html>
    """

    # Upload to S3 (overwrites if exists)
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=html_content,
        ContentType="text/html"
    )

    return {
        "statusCode": 200,
        "message": f"index.html uploaded to s3://{S3_BUCKET}/{S3_KEY}",
        "product_count": len(products)
    }
