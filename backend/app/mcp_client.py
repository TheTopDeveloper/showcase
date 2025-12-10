"""
MCP (Model Context Protocol) Client
====================================
Client for connecting to MCP server using Streamable HTTP.
"""

import json
import httpx
from typing import Dict, Any, List, Optional
from app.config import MCP_SERVER_URL


class MCPClient:
    """Client for MCP server communication."""
    
    def __init__(self, server_url: str = MCP_SERVER_URL):
        self.server_url = server_url
        self.client = httpx.Client(
            base_url=server_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30.0
        )
        self._initialized = False
    
    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an MCP JSON-RPC call."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        if params:
            request["params"] = params
        
        try:
            response = self.client.post("/mcp", json=request)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": {"code": -1, "message": str(e)}}
    
    def initialize(self) -> bool:
        """Initialize connection to MCP server."""
        if self._initialized:
            return True
        
        result = self._call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "customer-support-agent",
                "version": "1.0.0"
            }
        })
        
        if "error" not in result:
            self._initialized = True
            # Send initialized notification
            self._call("notifications/initialized", {})
            return True
        return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server."""
        if not self._initialized:
            self.initialize()
        
        result = self._call("tools/list")
        if "result" in result and "tools" in result["result"]:
            return result["result"]["tools"]
        return []
    
    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Call a tool on the MCP server."""
        if not self._initialized:
            self.initialize()
        
        if arguments is None:
            arguments = {}
        
        result = self._call("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in result:
            return f"Error calling {tool_name}: {result['error'].get('message', 'Unknown error')}"
        
        if "result" in result:
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                # MCP returns content as array of objects with type and text
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        text_parts.append(item.get("text", str(item)))
                    else:
                        text_parts.append(str(item))
                return "\n".join(text_parts)
            return str(result["result"])
        
        return f"No result from {tool_name}"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from MCP server."""
        if not self._initialized:
            self.initialize()
        
        result = self._call("resources/list")
        if "result" in result and "resources" in result["result"]:
            return result["result"]["resources"]
        return []
    
    def read_resource(self, uri: str) -> str:
        """Read a resource from MCP server."""
        if not self._initialized:
            self.initialize()
        
        result = self._call("resources/read", {"uri": uri})
        if "error" in result:
            return f"Error reading resource {uri}: {result['error'].get('message', 'Unknown error')}"
        
        if "result" in result:
            content = result["result"].get("contents", [])
            if content and len(content) > 0:
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        text_parts.append(item.get("text", str(item)))
                    else:
                        text_parts.append(str(item))
                return "\n".join(text_parts)
            return str(result["result"])
        
        return f"No content from resource {uri}"
    
    def close(self):
        """Close the client connection."""
        if hasattr(self, 'client'):
            self.client.close()


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the MCP client singleton."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        _mcp_client.initialize()
    return _mcp_client

