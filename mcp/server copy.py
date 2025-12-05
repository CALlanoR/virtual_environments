import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import traceback
import signal
import sys
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    logger.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded")

    # Log database configuration (without password)
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "postgres"),
        "user": os.getenv("DB_USER", "postgres"),
        "port": os.getenv("DB_PORT", "5432"),
    }
    logger.debug(f"Database configuration (excluding password): {db_config}")

    # Database connection parameters
    DB_CONFIG = {
        **db_config,
        "password": os.getenv("DB_PASSWORD", "your_password"),
    }

    # Test database connection before starting server
    logger.info("Testing database connection before server start...")
    try:
        with psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("Initial database connection test successful")
    except Exception as e:
        logger.error(f"Failed to connect to database during startup: {str(e)}")
        logger.error(f"Database connection error traceback: {traceback.format_exc()}")
        sys.exit(1)

    # Create an MCP server
    logger.info("Initializing MCP Server...")
    mcp = FastMCP("PostgreSQL Demo")
    logger.info("MCP Server initialized")

    def get_db_connection():
        """Create a database connection"""
        logger.info("Attempting database connection")
        try:
            logger.debug("Connecting with parameters: %s", {k: v for k, v in DB_CONFIG.items() if k != 'password'})
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            logger.info("Database connection successful")
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    @mcp.tool()
    def execute_query(query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict]:
        """Execute a PostgreSQL query and return results

        Args:
            query: SQL query to execute
            params: Optional tuple of parameters for the query

        Returns:
            List of dictionaries containing the query results
        """
        logger.info(f"Executing query: {query}")
        if params:
            logger.debug(f"Query parameters: {params}")
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    logger.info(
                        f"Query executed successfully, returned {len(results)} rows"
                    )
                    return results
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {"error": str(e)}

    @mcp.tool()
    def get_users() -> List[Dict]:
        """Get all users from the database"""
        logger.info("Fetching all users")
        query = "SELECT * FROM users"
        return execute_query(query)

    @mcp.tool()
    def get_conceptgroups(conceptgroup_id: int) -> List[Dict]:
        """Get concept groups by ID"""
        query = """
            SELECT
                conceptgroup_id,
                group_name,
                type,
                client_id,
                grp_type_id
            FROM
                allconcepts_omop_api.conceptgroups
            WHERE
                conceptgroup_id = %s
            ORDER BY
                conceptgroup_id ASC
            LIMIT
                100
        """
        return execute_query(query, (conceptgroup_id,))

    @mcp.resource("conceptgroups://{conceptgroup_id}")
    def get_conceptgroup(conceptgroup_id: int) -> List[Dict]:
        """Get a concept group by ID as a resource"""
        result = get_conceptgroups(conceptgroup_id=conceptgroup_id)
        return result

    logger.info("Server setup complete - ready to handle requests")

    # Get the underlying ASGI app from the FastMCP instance
    app = mcp.run(transport="streamable-http")

    # Start the ASGI server
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8080)

except Exception as e:
    logger.error(f"Failed to initialize server: {str(e)}")
    logger.error(f"Server initialization error traceback: {traceback.format_exc()}")
    sys.exit(1)
