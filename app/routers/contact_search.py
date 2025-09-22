# app/routes/contact_search.py
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.csrf import generate_csrf_token, validate_csrf_token
from app.models.contact import Contact
from app.models.user import User
from app.utils.email_utils import generate_email_patterns, verify_email
from app.utils.company_scraper import scrape_company_emails
from app.dependencies import get_current_user
import csv, io
import json
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# --------------------
# GET: Contact Search
# --------------------
@router.get("/contacts/search")
async def contact_search(
    request: Request,
    name: str = "",
    email: str = "",
    company: str = "",
    domain: str = "",
    search_mode: str = "all",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    contacts = []

    # 1️⃣ Search in DB
    if search_mode in ["all", "db"]:
        stmt = select(Contact)
        if name:
            stmt = stmt.filter(Contact.name.ilike(f"%{name}%"))
        if email:
            stmt = stmt.filter(Contact.email.ilike(f"%{email}%"))
        if company:
            stmt = stmt.filter(Contact.company_name.ilike(f"%{company}%"))
        result = await db.execute(stmt)
        db_results = result.scalars().all()
        for c in db_results:
            c.source = "DB"
        contacts.extend(db_results)

    # 2️⃣ Generate email patterns
    if search_mode in ["all", "pattern"] and name and (company or domain):
        domain_to_use = domain or company
        for p in generate_email_patterns(name, domain_to_use):
            contacts.append(Contact(
                name=name,
                email=p,
                company_name=company or "",
                source="Pattern"
            ))

    # 3️⃣ Verify email
    if search_mode in ["all", "verify"] and email:
        valid = verify_email(email)
        contacts.append(Contact(
            name=name or "",
            email=email,
            company_name=company or "",
            source="Verified" if valid else "Verify",
            email_valid=valid
        ))

    # 4️⃣ Scrape company/domain
    if search_mode in ["all", "domain"] and (company or domain):
        try:
            scraped = scrape_company_emails(company_name=company, domain=domain)
            for c in scraped:
                contacts.append(Contact(
                    name=c.get("name"),
                    title=c.get("title"),
                    email=c.get("email"),
                    phone=c.get("phone"),
                    company_name=c.get("company_name"),
                    location=c.get("location"),
                    source=c.get("source"),
                    email_valid=verify_email(c.get("email"))
                ))
        except Exception:
            pass

    # 5️⃣ Deduplicate contacts
    unique = {}
    for c in contacts:
        if not c.email:
            continue
        if c.email in unique:
            existing = unique[c.email]
            if c.source not in existing.source:
                existing.source = f"{existing.source}, {c.source}"
            if c.email_valid:
                existing.email_valid = True
            if not existing.name and c.name:
                existing.name = c.name
            if not existing.title and c.title:
                existing.title = c.title
            if not existing.phone and c.phone:
                existing.phone = c.phone
            if not existing.company_name and c.company_name:
                existing.company_name = c.company_name
            if not existing.location and c.location:
                existing.location = c.location
        else:
            unique[c.email] = c
    contacts = list(unique.values())

    csrf_token = generate_csrf_token(request)

    return templates.TemplateResponse("contact_search.html", {
        "request": request,
        "contacts": contacts,
        "name": name,
        "email": email,
        "company": company,
        "domain": domain,
        "search_mode": search_mode,
        "csrf_token": csrf_token,
        "user": user
    })


# --------------------
# POST: Bulk CSV Upload
# --------------------
@router.post("/contacts/search/bulk")
async def bulk_upload(
    request: Request,
    bulk_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contents = await bulk_file.read()
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8")))
    contacts = []

    for row in reader:
        contacts.append(Contact(
            name=row.get("name"),
            title=row.get("title"),
            email=row.get("email"),
            phone=row.get("phone"),
            company_name=row.get("company"),
            location=row.get("location"),
            source="Bulk Upload"
        ))

    # Deduplicate contacts
    unique = {}
    for c in contacts:
        if not c.email:
            continue
        if c.email in unique:
            existing = unique[c.email]
            if c.source not in existing.source:
                existing.source = f"{existing.source}, {c.source}"
            if c.email_valid:
                existing.email_valid = True
        else:
            unique[c.email] = c
    contacts = list(unique.values())

    csrf_token = generate_csrf_token(request)

    return templates.TemplateResponse("contact_search.html", {
        "request": request,
        "contacts": contacts,
        "name": "",
        "email": "",
        "company": "",
        "domain": "",
        "search_mode": "bulk",
        "csrf_token": csrf_token,
        "user": user  # guaranteed to exist
    })
