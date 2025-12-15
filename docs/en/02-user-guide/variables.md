# Variables System

TestGyver uses a powerful hierarchical variable system to manage configuration across different environments.

## Variable Types

### 1. Global Variables (Root)
*   Defined in **Admin > Variables**.
*   These are the default values if no environment-specific value overrides them.
*   Example: `api_url` = `http://localhost`

### 2. Environment Variables (Filière)
*   Overrides Global Variables for a specific environment (e.g., "Production", "Staging").
*   Selected when launching a campaign.
*   Example: `api_url` for "Production" = `https://api.example.com`

### 3. Collection Variables (System)
*   Automatically provided by the system during execution.
*   `{{test.test_id}}`: ID of the current test.
*   `{{test.campain_id}}`: ID of the current campaign.
*   `{{test.work_dir}}`: Path to the campaign's working directory.
*   `{{test.files_dir}}`: Path to the campaign's file storage.

### 4. Test Variables
*   Defined specifically for a single test case.
*   Useful for parameterized tests.
*   Accessed via `{{app.variable_name}}`.

## Resolution Logic

When a variable `{{my_var}}` is used in an action:

```mermaid
graph TD
    A[Start Resolution] --> B{Is defined in Test?}
    B -- Yes --> C[Use Test Value]
    B -- No --> D{Is defined in Environment?}
    D -- Yes --> E[Use Environment Value]
    D -- No --> F{Is defined in Root?}
    F -- Yes --> G[Use Root Value]
    F -- No --> H[Error / Unresolved]
```

## Managing Variables

Go to **Admin > Variables** to manage your configuration.
*   **Create Root**: Adds a new variable key.
*   **Add Environment Value**: Defines a value for an existing key in a specific environment.

## Variable Obfuscation

For security reasons, it is possible to mask the value of certain sensitive variables (passwords, API keys, tokens, etc.).

### How it works
*   When creating or editing a variable, check the **"Obfuscate value"** box.
*   The value will be masked in the administration interface (displayed as `*****`).
*   During test execution, the real value will be used, but it will be replaced by `*****` in the execution logs.

### Precautions
*   Obfuscation prevents accidental display in the interface and standard logs.
*   However, if a test is designed to explicitly export or display the value (e.g., writing the variable to an unsecured text file), the value could be exposed.
*   Ensure that your test scripts do not attempt to bypass this protection.
