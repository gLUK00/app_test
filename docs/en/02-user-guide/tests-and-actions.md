# Tests and Actions

A **Test** is a sequence of **Actions**. TestGyver executes these actions sequentially.

## Creating a Test

1.  Inside a Campaign, click **Add Test**.
2.  Provide a name and description.
3.  **Add Variables** (Optional): Define test-specific variables (e.g., `username`, `itemId`) that can be used in your actions.

## Adding Actions

Actions are the building blocks of your test.

1.  Click **Add Action**.
2.  **Select Action Type**: Choose from the available plugins (e.g., HTTP Request, SSH Command, Wait).
3.  **Configure Action**: Fill in the specific parameters for the chosen action.
![Action configuration form](../../assets/action_request.png)
> Action configuration form (e.g., HTTP Request) showing input fields.

### Variable Autocomplete
When typing in text fields, TestGyver suggests available variables:
![Variable autocomplete](../../assets/autocomplete.png)
> Autocomplete dropdown appearing while typing `{{` in a text field, showing colored suggestions.

*   <span style="color:blue">**Global Variables**</span>: `{{variable_name}}`
*   <span style="color:green">**Test Variables**</span>: `{{app.variable_name}}`
*   <span style="color:red">**Collection Variables**</span>: `{{test.test_id}}`, `{{test.files_dir}}`

### Output Variables
Some actions produce output (e.g., an HTTP response body).
*   These are displayed as **Output Variables** in the action configuration.
*   You can use them in subsequent actions within the same test.

## Ordering Actions
Actions are executed in the order they appear. You can reorder them using the drag-and-drop interface or up/down buttons (depending on UI version).

## Execution
You can run a single test directly from the Test Details page to verify its behavior before running the full campaign.
