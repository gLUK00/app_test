# Creating a New Action Plugin

This guide details the process of creating a new action plugin for TestGyver. Action plugins allow you to extend the application's capabilities by adding new types of automated tasks (e.g., database interaction, API calls, file manipulation).

## Prerequisites

*   Basic knowledge of Python.
*   Access to the `plugins/actions/` directory of the project.

## Step-by-Step Guide

### 1. Create the Plugin File

Create a new Python file in the `plugins/actions/` directory. The file name should be descriptive (e.g., `my_custom_action.py`).

### 2. Inherit from `ActionBase`

Your class must inherit from `ActionBase` and implement the required methods.

```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """Description of what your action does."""
    
    # Metadata
    plugin_name = "my_custom_action"  # Unique internal name
    label = "My Custom Action"        # Display name in UI
    version = "1.0.0"
    author = "Your Name"
```

### 3. Implement Required Methods

You need to implement the following methods:

#### `get_metadata(self)`

Returns basic information about the plugin.

```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Detailed description of the action."
        }
```

#### `validate_config(self, config)`

Validates the parameters provided by the user before execution.

```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "Target host is required")
        return (True, "")
```

#### `get_input_mask(self)`

Defines the UI form for configuring the action. Supported types: `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`.

```python
    def get_input_mask(self):
        return [
            {
                "name": "target_host",
                "type": "string",
                "label": "Target Host",
                "placeholder": "192.168.1.1",
                "required": True
            },
            {
                "name": "port",
                "type": "number",
                "label": "Port",
                "placeholder": 8080,
                "required": False
            }
        ]
```

#### `get_output_variables(self)`

Defines variables that this action will produce, which can be used by subsequent actions.

```python
    def get_output_variables(self):
        return [
            {
                "name": "execution_result",
                "description": "Result of the operation",
                "type": "string"
            }
        ]
```

#### `execute(self, context)`

The core logic of your action. The `context` object provides access to variables and environment data.

```python
    def execute(self, context):
        # Access input parameters
        host = context.get('target_host')
        
        # Perform your logic here
        try:
            # ... do something ...
            result = "Success"
            
            # Set output variables
            self.output_variables['execution_result'] = result
            
            return (0, ["Connected to " + host, "Operation successful"])
        except Exception as e:
            return (1, [f"Error: {str(e)}"])
```

### 4. Registration

The `PluginManager` automatically discovers plugins in the `plugins/actions/` directory. No manual registration is required. Just restart the application.

## Best Practices

*   **Error Handling**: Always wrap your execution logic in try/except blocks to prevent crashing the test runner.
*   **Logging**: Return detailed traces (second element of the return tuple) to help users debug issues.
*   **Validation**: Be strict in `validate_config` to catch errors early.

## Testing Your Plugin

To facilitate the development and testing of your plugins, a complete local environment is available via Docker Compose.

### 1. Start the Test Environment

A `test-docker-compose.yml` file is provided in the `init/` directory. It sets up various services (FTP, SFTP, WebDAV, SSH, S3/MinIO, HTTP API) to test your actions against real targets.

```bash
sudo docker-compose -f init/test-docker-compose.yml up -d
```

### 2. Import Test Data

To quickly populate your TestGyver instance with a comprehensive test campaign covering all standard actions:

1.  Go to the **Campaigns** page in the application.
2.  Click on **Import**.
3.  Select the file `init/campain_All_tests.json`.

This campaign contains examples of how to configure actions to interact with the services provided by the test environment.

### 3. Import Environment Variables

The test campaign relies on specific variables (hostnames, credentials, etc.). You can import them automatically using the provided script.

Ensure your virtual environment is active, then run:

```bash
python import_variables.py init/import-var-test-docker.json
```

This will create the necessary variables in the "Global" environment (or the one defined in the JSON file) to match the `test-docker-compose.yml` configuration.
