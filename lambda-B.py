import boto3
from bs4 import BeautifulSoup
import re

s3 = boto3.client("s3")

SOURCE_BUCKET = "testing-lambda-code-123"
DEST_BUCKET = "amazon-frontend-site-bucket"

def lambda_handler(event, context):

    html = s3.get_object(
        Bucket=SOURCE_BUCKET,
        Key="index.html"
    )["Body"].read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")

    lines = list(soup.stripped_strings)

    laptops = []
    current_name = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect laptop name
        if ("laptop" in line.lower()) or ("macbook" in line.lower()):
            current_name = line

        # Detect price ($298 + 84)
        if line.startswith("$") and current_name:
            price = line
            if i + 1 < len(lines) and lines[i + 1].isdigit():
                price = f"{line}.{lines[i + 1]}"
                i += 1

            laptops.append({
                "name": current_name,
                "price": price
            })
            current_name = None

        i += 1

    if not laptops:
        laptops.append({"name": "No laptops found", "price": "-"})

    # Build HTML table
    rows = "".join(
        f"<tr><td>{l['name']}</td><td>{l['price']}</td></tr>"
        for l in laptops
    )

    output_html = f"""
    <html>
    <head>
        <title>Laptop Prices</title>
    </head>
    <body>
        <h1>Laptop Prices</h1>
        <table border="1" cellpadding="8">
            <tr>
                <th>Laptop Name</th>
                <th>Price</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    s3.put_object(
        Bucket=DEST_BUCKET,
        Key="index.html",
        Body=output_html.encode("utf-8"),
        ContentType="text/html"
    )

    return {
        "status": "success",
        "laptops_found": len(laptops)
    }
