import re
import requests
from bs4 import BeautifulSoup
from app.utils.email_utils import generate_email_patterns, verify_email

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def scrape_company_emails(company_name: str, domain: str = None):
    contacts = []
    domain_to_use = domain or company_name.replace(" ", "").lower() + ".com"
    urls = [f"https://{domain_to_use}", f"https://www.{domain_to_use}"]

    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=5)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", soup.text))
            for e in emails:
                if verify_email(e):
                    contacts.append({
                        "name": "",
                        "title": "",
                        "email": e,
                        "phone": "",
                        "company_name": company_name,
                        "location": "",
                        "source": "Scraper"
                    })

        except Exception:
            continue

    if not contacts and company_name:
        patterns = generate_email_patterns(company_name, domain_to_use)
        for p in patterns:
            contacts.append({
                "name": "",
                "title": "",
                "email": p,
                "phone": "",
                "company_name": company_name,
                "location": "",
                "source": "Pattern"
            })

    return contacts
