# Dynamic Redirect

A lightweight Azure Function that intelligently routes users to Power Apps applications using dynamic URL redirection. Perfect for organizations managing multiple Power Apps environments that need a simplified access solution.

## Key Features

- **Smart URL Routing**: Automatically directs users to the correct Power Apps application based on the `app_name` parameter
- **Environment Prefix Support**: Detects environment prefixes (PRD, TST, DEV) in the app name to route to specific environments
- **Configuration File Based**: Uses a JSON file for application mappings
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
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "ENVIRONMENT_GUID": "your-environment-guid",
       "IS_GOV": "true"
     }
   }
   ```

   Then create an `app_mappings.json` file in the same directory as your `__init__.py`:

   ```json
   [
     {
       "AppName": "eprf",
       "Environments": {
         "PRD": "fa8add59-6ced-4077-a08e-896078f3b693",
         "TST": "fa8add59-test-4077-a08e-896078f3b693",
         "DEV": "fa8add59-dev-4077-a08e-896078f3b693"
       }
     },
     {
       "AppName": "cip",
       "Environments": {
         "PRD": "c877b27a-e163-4fd8-bddc-54ecc76ecd91",
         "TST": "c877b27a-test-4fd8-bddc-54ecc76ecd91",
         "DEV": "c877b27a-dev-4fd8-bddc-54ecc76ecd91"
       }
     }
   ]
   ```

   > ⚠️ Important: Add local.settings.json to your .gitignore file to prevent committing sensitive information.

3. **Configure Azure Function App Settings**
   When deploying to Azure, configure the following application settings:
   - `ENVIRONMENT_GUID`: Your Power Apps environment identifier
   - `IS_GOV`: Set to "true" for .gov environments, "false" otherwise
   - Ensure your `app_mappings.json` file is deployed with your function code

4. **Test Locally**
   - Install [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
   - Run `func start` to start the local development server

5. **Deploy to Azure**
   Follow the [official deployment guide](https://learn.microsoft.com/azure/azure-functions/functions-deployment-technologies)

## Usage

### Making Requests

Send a GET request to the function endpoint:

```http
GET /api/redirect?app_name=YourAppName
```

To target a specific environment (PRD, TST, DEV), add the environment prefix to the app name:

```http
GET /api/redirect?app_name=PRDYourAppName
GET /api/redirect?app_name=TSTYourAppName
GET /api/redirect?app_name=DEVYourAppName
```

Additional query parameters can be passed and will be forwarded to the Power App:

```http
GET /api/redirect?app_name=TSTYourAppName&param1=value1&param2=value2
```

All query parameters (except `app_name`) will be preserved and passed through to the target Power App URL.

### Example Requests

1. Basic redirect (defaults to PRD environment):

   ```http
   GET /api/redirect?app_name=cip
   ```

2. Environment-specific redirect:

   ```http
   GET /api/redirect?app_name=TSTcip
   ```

   This will redirect to the CIP app in the TST environment.

3. Redirect with additional parameters:

   ```http
   GET /api/redirect?app_name=DEVeprf&user_id=12345&view=summary
   ```

   This will redirect to the EPRF app in the DEV environment while preserving `user_id` and `view` parameters.

### Response Types

| Status Code | Description | Example Scenario |
|-------------|-------------|------------------|
| 302 | Successful redirect to Power Apps | Valid app_name provided |
| 400 | Missing app_name parameter | No app_name in query string |
| 404 | Application not found | Invalid app_name or environment not supported |
| 500 | Server configuration error | Missing environment variables or JSON file |

## Configuration Details

The function requires two types of configuration:

1. **Environment Variables**:
   - `ENVIRONMENT_GUID`: Your Power Apps environment identifier
   - `IS_GOV`: Boolean flag for .gov domain usage ("true" or "false")

2. **JSON Configuration File**:
   - `app_mappings.json`: Contains mappings for applications and their environment-specific GUIDs

Example app_mappings.json:

```json
[
  {
    "AppName": "SalesApp",
    "Environments": {
      "PRD": "12345678-abcd-1234-efgh-1234567890ab",
      "TST": "87654321-abcd-4321-efgh-0987654321zy",
      "DEV": "abcdef12-3456-7890-abcd-ef1234567890"
    }
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

2. Set up local.settings.json and app_mappings.json with your configuration

3. Start the function locally:

   ```bash
   func start
   ```

4. Test using curl or Postman:

   ```bash
   curl "http://localhost:7071/api/redirect?app_name=TSTYourAppName"
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