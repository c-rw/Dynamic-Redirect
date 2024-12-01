# Dynamic Redirect

A lightweight Azure Function that intelligently routes users to Power Apps applications using dynamic URL redirection. Perfect for organizations managing multiple Power Apps environments that need a simplified access solution.

## Key Features

- **Smart URL Routing**: Automatically directs users to the correct Power Apps application based on the `app_name` parameter
- **Configuration via JSON**: Simple application mapping management through a centralized `AppMappings.json` file
- **Environment Flexibility**: Supports both commercial and government (.gov) Power Apps environments
- **Robust Error Handling**: Provides clear, actionable feedback for common request scenarios

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/c-rw/DynamicRedirector.git
   cd DynamicRedirector
   ```

2. **Configure Your Environment**
   Create an `AppMappings.json` file in the root directory:
   ```json
   {
     "environment_guid": "your-environment-guid",
     "is_gov": false,
     "app_mappings": [
       {
         "AppName": "YourAppName",
         "AppGUID": "your-app-guid"
       }
     ]
   }
   ```

3. **Test Locally**
   - Install [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
   - Run `func start` to start the local development server

4. **Deploy to Azure**
   Follow the [official deployment guide](https://learn.microsoft.com/azure/azure-functions/functions-deployment-technologies)

## Usage

### Making Requests

Send a GET request to the function endpoint:
```http
GET /api/redirector?app_name=YourAppName
```

### Response Types

| Status Code | Description | Example Scenario |
|-------------|-------------|------------------|
| 302 | Successful redirect to Power Apps | Valid app_name provided |
| 400 | Missing app_name parameter | No app_name in query string |
| 404 | Application not found | Invalid app_name provided |
| 500 | Server configuration error | JSON mapping file issues |

## Configuration Details

The `AppMappings.json` file requires three key components:

- `environment_guid`: Your Power Apps environment identifier
- `is_gov`: Boolean flag for .gov domain usage
- `app_mappings`: Array of application mappings containing:
  - `AppName`: The friendly name used in requests
  - `AppGUID`: The Power Apps application GUID

Example:
```json
{
    "environment_guid": "12345678-1234-1234-1234-123456789012",
    "is_gov": false,
    "app_mappings": [
        {
            "AppName": "SalesApp",
            "AppGUID": "87654321-4321-4321-4321-210987654321"
        }
    ]
}
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

2. Start the function locally:
   ```bash
   func start
   ```

3. Test using curl or Postman:
   ```bash
   curl "http://localhost:7071/api/redirector?app_name=YourAppName"
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please:

1. Check existing [issues](https://github.com/c-rw/DynamicRedirector/issues)
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
