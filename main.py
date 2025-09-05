import asyncio
from contextlib import asynccontextmanager
from src.scheduler.fund_schema import SchedulerHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.routers import all_routers


from src.config import ModuleConfig



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(SchedulerHandler().update_portfolios_task())
    yield
    # Clean up
    task.cancel()


app = FastAPI(
    title=f"{ModuleConfig.APP_NAME}",
    description="",
    version=ModuleConfig.MODULE_VERSION,
    contact={
        "name": "Hemanth Kumar Pasham",
        "email": "hemanthkumarpasham9502@gmail.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.include_router(all_routers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ModuleConfig.CORS_ORIGINS,  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns a simple message indicating the API is healthy.
    """
    return {"status": "healthy", "message": f"{ModuleConfig.APP_NAME} is running!"}

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that provides a welcome message.
    Returns a simple message indicating the API is running.
    """
    return {"message": f"Welcome to the {ModuleConfig.APP_NAME}!"}
