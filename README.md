# Dynamic Redirect

A lightweight Azure Function that intelligently routes users to Power Apps applications using dynamic URL redirection. Perfect for organizations managing multiple Power Apps environments that need a simplified access solution.

## Key Features

- **Smart URL Routing**: Automatically directs users to the correct Power Apps application based on the `app_name` parameter
- **Environment-based Configuration**: Uses environment variables for secure configuration management
- **Environment Flexibility**: Supports both commercial and government (.gov) Power Apps environments
- **Robust Error Handling**: Provides clear, actionable feedback for common request scenarios

## Quick Start

1. **Clone the Repository**

   ```bash
   git clone https://github.com/c-rw/Dynamic-Redirect.git
   cd Dynamic-Redirect
   ```

2. **Configure Your Environment**
   Create a `local.settings.json` file in the root directory:

   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "ENVIRONMENT_GUID": "your-environment-guid",
       "IS_GOV": "true",
       "APP_MAPPINGS": "[{\"AppName\": \"YourAppName\", \"AppGUID\": \"your-app-guid\"}]"
     }
   }
   ```

   > ⚠️ Important: Add local.settings.json to your .gitignore file to prevent committing sensitive information.

3. **Configure Azure Function App Settings**
   When deploying to Azure, configure the following application settings:
   - `ENVIRONMENT_GUID`: Your Power Apps environment identifier
   - `IS_GOV`: Set to "true" for .gov environments, "false" otherwise
   - `APP_MAPPINGS`: JSON string containing app name to GUID mappings

4. **Test Locally**
   - Install [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
   - Run `func start` to start the local development server

5. **Deploy to Azure**
   Follow the [official deployment guide](https://learn.microsoft.com/azure/azure-functions/functions-deployment-technologies)

## Usage

### Making Requests

Send a GET request to the function endpoint:

```http
GET /api/redirector?app_name=YourAppName
```

Additional query parameters can be passed and will be forwarded to the Power App:

```http
GET /api/redirector?app_name=YourAppName&param1=value1&param2=value2
```

All query parameters (except `app_name`) will be preserved and passed through to the target Power App URL.

### Example Requests

1. Basic redirect:

   ```http
   GET /api/redirector?app_name=SalesApp
   ```

2. Redirect with additional parameters:

   ```http
   GET /api/redirector?app_name=SalesApp&user_id=12345&view=summary
   ```

   This will redirect to the SalesApp while preserving `user_id` and `view` parameters.

### Response Types

| Status Code | Description | Example Scenario |
|-------------|-------------|------------------|
| 302 | Successful redirect to Power Apps | Valid app_name provided |
| 400 | Missing app_name parameter | No app_name in query string |
| 404 | Application not found | Invalid app_name provided |
| 500 | Server configuration error | Missing environment variables |

## Configuration Details

The function requires three environment variables:

1. `ENVIRONMENT_GUID`: Your Power Apps environment identifier
2. `IS_GOV`: Boolean flag for .gov domain usage ("true" or "false")
3. `APP_MAPPINGS`: JSON string array of application mappings containing:
   - `AppName`: The friendly name used in requests
   - `AppGUID`: The Power Apps application GUID

Example APP_MAPPINGS:

```json
[
    {
        "AppName": "SalesApp",
        "AppGUID": "87654321-4321-4321-4321-210987654321"
    }
]
```

## Development

### Prerequisites

- Azure Functions Core Tools
- Azure subscription
- Basic knowledge of Power Apps environments
- Python 3.6 or higher

### Local Development

1. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Set up local.settings.json with your configuration

3. Start the function locally:

   ```bash
   func start
   ```

4. Test using curl or Postman:

   ```bash
   curl "http://localhost:7071/api/redirector?app_name=YourAppName"
   ```

### Environment Variable Management

For production deployments, consider using:

- Azure Key Vault for sensitive configuration
- Azure App Configuration for feature flags and app settings
- Managed Identities for secure access to Azure resources

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please:

1. Check existing [issues](https://github.com/c-rw/Dynamic-Redirect/issues)
2. Create a new issue with detailed reproduction steps
3. Include relevant logs and configuration (sanitized of sensitive data)

## Author

**Chris Worth**

- Website: [chrisworth.dev](https://chrisworth.dev)
- GitHub: [@c-rw](https://github.com/c-rw)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2024 Chris Worth

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
