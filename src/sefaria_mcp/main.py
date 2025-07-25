from fastapi import FastAPI
from fastmcp import FastMCP

# Local imports
from .resources import register_resources
from .tools import register_tools

# ---------------------------------------------------------------------------
# Create the FastMCP server instance. Giving the server a descriptive name is
# recommended for easier discovery when multiple MCP servers are running.
# ---------------------------------------------------------------------------

mcp = FastMCP("Sefaria MCP 📚")

# Register resources and tools defined in separate modules. This keeps the
# top-level file small while still using the recommended `@mcp.tool` /
# `@mcp.resource` decorators inside those modules.
register_resources(mcp)
register_tools(mcp)

# ---------------------------------------------------------------------------
# Dual transport setup for backwards compatibility
# ---------------------------------------------------------------------------
# Create both SSE (legacy) and HTTP (modern) transport apps
sse_app = mcp.http_app(transport="sse")     # Legacy SSE transport
http_app = mcp.http_app(transport="http")   # Modern HTTP streaming transport

# Mount both transports on a single FastAPI app
app = FastAPI(title="Sefaria MCP Server", version="1.0.0")
app.mount("/sse", sse_app)    # Legacy: GET /sse (backwards compatible)
app.mount("/mcp", http_app)   # Modern: POST /mcp (recommended for new clients)
app.router.redirect_slashes = False

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "transports": ["sse", "http"]}

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main() -> None:  # pragma: no cover – simple wrapper for console_scripts
    import uvicorn
    uvicorn.run("sefaria_mcp.main:app", host="0.0.0.0", port=8088, reload=False)

if __name__ == "__main__":
    main() 
