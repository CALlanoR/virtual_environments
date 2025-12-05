import pytest
from mcp.server.fastmcp import FastMCP
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import mcp, execute_query, get_users

@pytest.fixture
def test_mcp():
    """Create a test MCP instance"""
    return mcp

def test_mcp_initialization(test_mcp):
    """Test that MCP server is initialized correctly"""
    assert isinstance(test_mcp, FastMCP)
    assert test_mcp.name == "PostgreSQL Demo"

def test_execute_query_exists(test_mcp):
    """Test that execute_query function exists"""
    assert callable(execute_query)

def test_get_users_exists(test_mcp):
    """Test that get_users function exists"""
    assert callable(get_users)

@pytest.mark.asyncio
async def test_execute_query_with_version():
    """Test execute_query with a simple version query"""
    result = execute_query("SELECT version()")
    assert isinstance(result, (list, dict))
    if isinstance(result, dict):
        assert "error" not in result

@pytest.mark.asyncio
async def test_get_users_returns_list():
    """Test get_users returns a list"""
    result = get_users()
    assert isinstance(result, (list, dict))
    if isinstance(result, dict):
        assert "error" not in result 