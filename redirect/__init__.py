import json
import logging
import os
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import azure.functions as func

# Configure logging
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

@lru_cache(maxsize=1)
def load_config() -> Tuple[str, bool, List[Dict[str, str]]]:
    """Load and cache configuration from environment variables.
    
    Returns:
        Tuple[str, bool, List[Dict[str, str]]]: Tuple containing:
            - environment_guid: The environment GUID
            - is_gov: Boolean flag for .gov domain usage
            - mappings: List of application mapping dictionaries
        
    Raises:
        ConfigError: If required configuration is missing
    """
    try:
        # Get environment variables
        environment_guid = os.environ.get('ENVIRONMENT_GUID')
        is_gov = os.environ.get('IS_GOV', 'false').lower() == 'true'
        app_mappings_str = os.environ.get('APP_MAPPINGS')

        if not environment_guid:
            raise ConfigError("ENVIRONMENT_GUID environment variable not found")
        if not app_mappings_str:
            raise ConfigError("APP_MAPPINGS environment variable not found")

        try:
            mappings = json.loads(app_mappings_str)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Failed to parse APP_MAPPINGS JSON: {str(e)}")

        logger.info(
            f"Successfully loaded configuration with {len(mappings)} mappings"
        )
        return environment_guid, is_gov, mappings

    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise ConfigError(f"Failed to load configuration: {str(e)}")

def get_mapping(app_name: str) -> Optional[Dict[str, str]]:
    """Get mapping for a specific app name using cached configuration.
    
    Args:
        app_name: Name of the application to look up
        
    Returns:
        Optional[Dict[str, str]]: Mapping dictionary if found, None otherwise
    """
    try:
        _, _, mappings = load_config()
        return next((m for m in mappings if m["AppName"] == app_name), None)
    except ConfigError as e:
        logger.error(f"Error retrieving mapping for {app_name}: {e}")
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handle redirection requests.
    
    Args:
        req: The HTTP request object
        
    Returns:
        func.HttpResponse: The response with appropriate status code and headers
    """
    start_time = time.time()
    request_id = f"{int(start_time)}-{os.urandom(4).hex()}"
    logger.info("Redirector function processed a request", 
                extra={"request_id": request_id})

    try:
        # Load configuration
        try:
            environment_guid, is_gov, _ = load_config()
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            return func.HttpResponse(
                "Service configuration error",
                status_code=500
            )

        # Get and validate app name
        app_name = req.params.get("app_name")
        if not app_name:
            return func.HttpResponse(
                "Please provide an app_name in the query string.",
                status_code=400
            )

        # Extract all query parameters, except the mandatory 'app_name'
        params = req.params.copy()
        params.pop("app_name", None)

        # Build the query string from remaining parameters
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])

        # Construct base URL using environment configuration
        base_url = f"https://apps.{'gov.' if is_gov else ''}powerapps{'.us' if is_gov else '.com'}/play/e"

        # Get mapping using cached function
        mapping = get_mapping(app_name)
        if not mapping:
            logger.warning(f"App '{app_name}' not found",
                         extra={"request_id": request_id})
            return func.HttpResponse(
                f"App '{app_name}' not found.",
                status_code=404
            )

        # Construct redirect URL
        app_guid = mapping.get("AppGUID")
        redirect_url = f"{base_url}/{environment_guid}/a/{app_guid}"
        
        # Append query string if present
        if query_string:
            redirect_url = f"{redirect_url}?{query_string}"
            logger.info(f"Adding query parameters: {query_string}", 
                       extra={"request_id": request_id})

        logger.info(f"Redirecting to: {redirect_url}", 
                   extra={"request_id": request_id})
        
        return func.HttpResponse(
            status_code=302,
            headers={"Location": redirect_url}
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", 
                    extra={"request_id": request_id}, 
                    exc_info=True)
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )

    finally:
        end_time = time.time()
        logger.info(f"Request completed in {end_time - start_time:.3f} seconds",
                   extra={"request_id": request_id})