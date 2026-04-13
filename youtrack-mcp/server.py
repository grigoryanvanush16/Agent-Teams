import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("youtrack_mcp")

if __name__ == "__main__":
    transport = "http" if "--http" in sys.argv else "stdio"
    port = 8080
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()
