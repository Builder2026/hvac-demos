import subprocess
import sys

# Ensure dependencies are installed
subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl", "--user", "-q"])

import re
import math
import random
import os
import pandas as pd

NAMES = ["James", "Linda", "Michael", "Barbara", "Robert", "Patricia", "David", "Jennifer", "William", "Mary",
         "Carlos", "Susan", "Kevin", "Angela", "Brian", "Melissa", "Tony", "Rachel", "Greg", "Diane"]

REVIEW_TEXTS = [
    "Our {unit} went out on a {adj} day and they came out same-day. Tech was knowledgeable, had the part on the truck, and got us back up and running in under two hours. Price was very reasonable too.",
    "Called first thing in the morning and had a technician at my door by noon. Fixed the {unit} quickly and walked me through what had gone wrong. Super professional and no surprises on the bill.",
    "These guys saved us. {unit} stopped working right before the weekend and they still made time to come out. Fast, clean, and friendly. Didn't try to upsell me on anything I didn't need.",
    "I've used a few HVAC companies over the years and this is by far the best experience I've had. The tech who serviced our {unit} was on time, thorough, and explained everything clearly.",
    "Honest, reliable, and fairly priced. Had them out to look at our {unit} and they gave me a straight answer instead of trying to push a full replacement. Really appreciated the transparency.",
    "Booked online, got a confirmation call within the hour, tech showed up on time. Our {unit} had a refrigerant issue and it was handled cleanly. Will absolutely use them again.",
    "Our {unit} had been making a noise for weeks. They diagnosed it fast and had it fixed the same visit. Would highly recommend to anyone in the area looking for honest HVAC work.",
    "Very impressed with the whole experience. The technician took time to explain the issue with our {unit} and gave me options before doing anything. Felt like I was in good hands.",
]

UNITS = ["AC unit", "furnace", "heat pump", "HVAC system", "air handler", "central air unit"]
ADJS = ["sweltering", "freezing", "brutally hot", "bitter cold", "scorching"]

REVIEW_DATES = [
    "2 weeks ago", "1 month ago", "3 weeks ago", "2 months ago", "1 week ago",
    "last month", "3 months ago", "4 weeks ago",
]


def random_review():
    name = random.choice(NAMES)
    text = random.choice(REVIEW_TEXTS).format(unit=random.choice(UNITS), adj=random.choice(ADJS))
    initial = name[0] + "."
    date = random.choice(REVIEW_DATES)
    return {"text": text, "name": name, "initial": initial, "date": date}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def stars_html(rating):
    try:
        count = round(float(rating))
    except (ValueError, TypeError):
        count = 5
    return "★" * count


def clean_phone_raw(phone):
    return re.sub(r"[^\d+]", "", str(phone))


def default_email(name):
    slug = slugify(name).replace("-", "")
    return f"info@{slug}.com"


def main():
    leads_path = "leads.xlsx"
    template_path = "template.html"
    output_dir = "output"

    if not os.path.exists(leads_path):
        print(f"Error: {leads_path} not found.")
        sys.exit(1)

    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_excel(leads_path)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Filter rows with no website
    no_website = df[df["website"].isna() | (df["website"].astype(str).str.strip() == "")]

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    count = 0
    for _, row in no_website.iterrows():
        name = str(row.get("name", "")).strip()
        if not name:
            continue

        city = str(row.get("city", "")).strip()
        phone = str(row.get("phone", "")).strip()
        address = str(row.get("address", "")).strip()
        rating = row.get("rating", 5)
        reviews_raw = row.get("reviews", 0)
        try:
            review_count = int(float(reviews_raw))
        except (ValueError, TypeError):
            review_count = 0

        email_val = str(row.get("email", "")).strip()
        email = email_val if email_val and email_val.lower() != "nan" else default_email(name)

        name_short = name.split()[0]

        html = template
        html = html.replace("{{BUSINESS_NAME}}", name)
        html = html.replace("{{BUSINESS_NAME_SHORT}}", name_short)
        html = html.replace("{{CITY}}", city)
        html = html.replace("{{PHONE}}", phone)
        html = html.replace("{{PHONE_RAW}}", clean_phone_raw(phone))
        html = html.replace("{{RATING}}", str(rating))
        html = html.replace("{{REVIEW_COUNT}}", str(review_count))
        html = html.replace("{{STARS_HTML}}", stars_html(rating))
        html = html.replace("{{EMAIL}}", email)
        html = html.replace("{{ADDRESS}}", address)

        # Replace review placeholders
        for i in range(1, 4):
            review = random_review()
            html = html.replace(f"{{{{REVIEW_{i}_TEXT}}}}", review["text"])
            html = html.replace(f"{{{{REVIEW_{i}_NAME}}}}", review["name"])
            html = html.replace(f"{{{{REVIEW_{i}_INITIAL}}}}", review["initial"])
            html = html.replace(f"{{{{REVIEW_{i}_DATE}}}}", review["date"])

        filename = f"{slugify(city)}-{slugify(name)}.html"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print(f"  Generated: {filename}")

    print(f"\nDone. {count} file(s) generated in '{output_dir}/'.")


if __name__ == "__main__":
    main()
