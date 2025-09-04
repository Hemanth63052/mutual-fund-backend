import uvicorn
from src.config import ModuleConfig

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=ModuleConfig.HOST,
        port=ModuleConfig.PORT,
        reload=ModuleConfig.RELOAD_ASGI,
    )
