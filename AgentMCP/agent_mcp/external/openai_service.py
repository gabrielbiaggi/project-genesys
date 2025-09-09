# Agent-MCP/mcp_template/mcp_server_src/external/openai_service.py
import os
from typing import Optional  # Added import for Optional

# Import OpenAI library.
# It's good practice to handle potential ImportError if it's an optional dependency,
# though for this project, it seems to be a core requirement.
try:
    import openai
except ImportError:
    # If openai library is not installed, log an error and make client None.
    # The application might still run if RAG/OpenAI features are optional
    # and guarded by checks for a valid client.
    from ..core.config import (
        logger as temp_logger,
    )  # Use temp logger if config not fully up

    temp_logger.error(
        "OpenAI Python library not found. Please install it using 'pip install openai'. OpenAI dependent features will be unavailable."
    )
    openai = None  # Make openai None so subsequent checks fail gracefully

# Import configurations and global variables
from ..core.config import (
    logger,
)  # Removed OPENAI_API_KEY_ENV - it's defined locally below

# The openai_client instance will be stored in g.openai_client_instance
# g.openai_client_instance: Optional[openai.OpenAI] = None # This is defined in globals.py

# Optional environment variables
OPENAI_API_KEY_ENV = os.environ.get("OPENAI_API_KEY")

# Global OpenAI client instance, initialized on first use
openai_client: Optional[openai.OpenAI] = None
# Flag to prevent re-initialization
_openai_initialized = False

# Original location: main.py lines 173-177 (API key check)
# Original location: main.py lines 187-197 (get_openai_client function)


def initialize_openai_client() -> Optional[openai.OpenAI]:
    """
    Initializes and returns the OpenAI client.
    Returns None if the API key is not available.
    """
    global openai_client, _openai_initialized
    if _openai_initialized:
        return openai_client

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning(
            "OPENAI_API_KEY not found in environment. OpenAI features will be disabled."
        )
        _openai_initialized = True
        return None

    try:
        openai_client = openai.OpenAI(api_key=api_key)
        # Perform a simple test call to ensure the key is valid
        # openai_client.models.list()
        logger.info("OpenAI client initialized successfully.")
        _openai_initialized = True
        return openai_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
        openai_client = None
        _openai_initialized = True
        return None


def get_openai_client() -> Optional[openai.OpenAI]:
    """
    Returns the globally initialized OpenAI client instance.
    If the client is not initialized, it attempts to initialize it.
    """
    # It is assumed that initialize_openai_client has been called at startup.
    return openai_client


# Any other OpenAI specific helper functions that don't belong in RAG or tools
# could go here. For example, if you had a generic text generation or embedding
# function used by multiple parts of the system outside of the RAG context.
# For now, client initialization and access are the main concerns.

# Example of how this is intended to be used at startup:
# In server_lifecycle.py or cli.py:
# from mcp_server_src.external.openai_service import initialize_openai_client
# initialize_openai_client()
#
# Then, in other modules (e.g., RAG indexing, RAG tool):
# from mcp_server_src.external.openai_service import get_openai_client
# client = get_openai_client()
# if client:
#     # Use the client
# else:
#     # Handle OpenAI unavailability
