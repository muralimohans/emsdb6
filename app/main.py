from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routers import email_routes, auth, bulk_routes, dashboard_routes, multiple_routes, batch_routes, single_routes, contact_search, account_settings
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import URLSafeSerializer
from app.config import settings
from app.database import Base, engine

app = FastAPI(title="Email Validation System")

# Set up the templates directory
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
csrf_serializer = URLSafeSerializer(settings.secret_key, salt="csrf-token")

# -----------------------------
# Startup / Shutdown Events
# -----------------------------
@app.on_event("startup")
async def on_startup():
    # Create all tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Server started.")


@app.on_event("shutdown")
async def on_shutdown():
    print("Server shutting down.")


# Include router
app.include_router(auth.router)
app.include_router(dashboard_routes.router)
app.include_router(email_routes.router)
app.include_router(multiple_routes.router)
app.include_router(bulk_routes.router)
app.include_router(batch_routes.router)
app.include_router(single_routes.router)
app.include_router(contact_search.router)
app.include_router(account_settings.router)

# Homepage route
@app.get("/", response_class=HTMLResponse)
async def read_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/services")
async def services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

@app.get("/features")
async def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/buy-credits")
async def credits(request: Request):
    return templates.TemplateResponse("buy_credits.html", {"request": request})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render/Railway PORT or default 8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
