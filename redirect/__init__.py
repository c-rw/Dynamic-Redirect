import json
import logging
import os
import re
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import azure.functions as func

# Configure logging
logger = logging.getLogger(__name__)

# Define supported environments
SUPPORTED_ENVIRONMENTS = ["PRD", "TST", "DEV"]

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

@lru_cache(maxsize=1)
def load_config() -> Tuple[str, bool, List[Dict[str, any]]]:
    """Load and cache configuration from environment variables and JSON file.
    
    Returns:
        Tuple[str, bool, List[Dict[str, any]]]: Tuple containing:
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
        
        if not environment_guid:
            raise ConfigError("ENVIRONMENT_GUID environment variable not found")

        # Load app mappings from JSON file in script root
        script_dir = os.path.dirname(os.path.realpath(__file__))
        mappings_file_path = os.path.join(script_dir, 'app_mappings.json')
        
        try:
            with open(mappings_file_path, 'r') as f:
                mappings = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"App mappings file not found at {mappings_file_path}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Failed to parse app mappings JSON file: {str(e)}")
        except Exception as e:
            raise ConfigError(f"Error reading app mappings file: {str(e)}")

        logger.info(
            f"Successfully loaded configuration with {len(mappings)} mappings"
        )
        return environment_guid, is_gov, mappings

    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise ConfigError(f"Failed to load configuration: {str(e)}")

def parse_app_name(app_name_with_env: str) -> Tuple[str, str]:
    """Parse the app name with environment prefix.
    
    Args:
        app_name_with_env: App name with environment prefix (e.g., PRDcip, TSTeprf)
        
    Returns:
        Tuple[str, str]: Tuple containing environment and app name
    """
    # Check for valid format
    if len(app_name_with_env) < 4:
        return "PRD", app_name_with_env  # Default to PRD if no prefix
    
    # Extract first three characters as potential environment prefix
    potential_env = app_name_with_env[:3].upper()
    app_name = app_name_with_env[3:]
    
    # Validate environment
    if potential_env in SUPPORTED_ENVIRONMENTS:
        return potential_env, app_name
    else:
        return "PRD", app_name_with_env  # Default to PRD if prefix is not recognized

def get_mapping(app_name_with_env: str) -> Optional[Dict[str, str]]:
    """Get mapping for a specific app name using cached configuration.
    
    Args:
        app_name_with_env: App name possibly with environment prefix
        
    Returns:
        Optional[Dict[str, str]]: Mapping dictionary if found, None otherwise
    """
    try:
        env_prefix, app_name = parse_app_name(app_name_with_env)
        _, _, mappings = load_config()
        
        # Find the app in mappings
        app_mapping = next((m for m in mappings if m["AppName"] == app_name), None)
        
        if not app_mapping:
            logger.warning(f"App '{app_name}' not found in mappings")
            return None
            
        # Get the environment-specific GUID
        environments = app_mapping.get("Environments", {})
        app_guid = environments.get(env_prefix)
        
        if not app_guid:
            logger.warning(f"Environment '{env_prefix}' not found for app '{app_name}'")
            return None
            
        return {
            "AppName": app_name,
            "Environment": env_prefix,
            "AppGUID": app_guid
        }
        
    except ConfigError as e:
        logger.error(f"Error retrieving mapping for {app_name_with_env}: {e}")
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
        app_name_with_env = req.params.get("app_name")
        if not app_name_with_env:
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
        mapping = get_mapping(app_name_with_env)
        if not mapping:
            logger.warning(f"App '{app_name_with_env}' not found or environment not supported",
                         extra={"request_id": request_id})
            return func.HttpResponse(
                f"App '{app_name_with_env}' not found or environment not supported.",
                status_code=404
            )

        # Log the resolved environment and app
        env_prefix = mapping.get("Environment")
        app_name = mapping.get("AppName")
        logger.info(f"Resolved app request to {env_prefix} environment for app {app_name}",
                   extra={"request_id": request_id})

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