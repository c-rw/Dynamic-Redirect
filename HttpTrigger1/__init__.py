import json
import logging
import os
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import azure.functions as func

# Configure logging
logger = logging.getLogger(__name__)


class MappingError(Exception):
    """Custom exception for mapping-related errors."""
    pass


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass


@lru_cache(maxsize=1)
def load_config() -> Tuple[str, bool, List[Dict[str, str]]]:
    """Load and cache configuration and mappings from JSON file.
    
    Returns:
        Tuple[str, bool, List[Dict[str, str]]]: Tuple containing:
            - environment_guid: The environment GUID
            - is_gov: Boolean flag for .gov domain usage
            - mappings: List of application mapping dictionaries
        
    Raises:
        ConfigError: If required configuration is missing
        MappingError: If there's an error loading or parsing the mappings file
    """
    try:
        mappings_file = os.path.join(os.path.dirname(__file__), "AppMappings.json")
        if not os.path.exists(mappings_file):
            logger.error("AppMappings.json not found")
            raise ConfigError("Configuration file not found")

        with open(mappings_file, "r") as f:
            config = json.load(f)

        # Validate required configuration
        if "environment_guid" not in config:
            raise ConfigError("environment_guid not found in configuration")
        if "is_gov" not in config:
            raise ConfigError("is_gov not found in configuration")
        if "app_mappings" not in config:
            raise ConfigError("app_mappings not found in configuration")

        environment_guid = config["environment_guid"]
        is_gov = config["is_gov"]
        mappings = config["app_mappings"]

        logger.info(
            f"Successfully loaded configuration with {len(mappings)} mappings"
        )
        return environment_guid, is_gov, mappings

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise MappingError(f"Failed to parse configuration file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise MappingError(f"Failed to load configuration: {str(e)}")


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
    except (ConfigError, MappingError) as e:
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
        except (ConfigError, MappingError) as e:
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

        # Construct and return redirect response
        app_guid = mapping.get("AppGUID")
        redirect_url = f"{base_url}/{environment_guid}/a/{app_guid}"
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