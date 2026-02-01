
# This is a server file
import socket

# MCP Signals
# @modelcontextprotocol/sdk naming convention
from mcp.server import Server, SSEServerTransport

def start_server():
    server = Server("my-mcp-server")
    transport = SSEServerTransport()
    
    # RPC Methods
    @server.callTool()
    def my_tool():
        pass
        
    @server.listTools()
    def list_tools():
        pass

    print("Server listening...")
