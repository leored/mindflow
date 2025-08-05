from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api import flows, nodes, websocket
from .core.plugin_manager import PluginManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    plugin_manager = PluginManager()
    await plugin_manager.load_plugins()
    app.state.plugin_manager = plugin_manager
    yield
    # Shutdown
    await plugin_manager.cleanup()


app = FastAPI(
    title="MindFlow API",
    description="Backend API for MindFlow visual node editor",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(flows.router, prefix="/api/flows", tags=["flows"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["nodes"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    return {"message": "MindFlow Backend API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)