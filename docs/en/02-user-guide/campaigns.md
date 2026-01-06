# Managing Campaigns

A **Campaign** is a logical grouping of tests designed to validate a specific feature or workflow.

## Creating a Campaign

1.  From the Dashboard, click **Add Campaign**.
2.  Fill in the details:
    *   **Name**: A unique name for your campaign.
    *   **Description**: Optional details about the campaign's purpose.
3.  Click **Save**. You will be redirected to the Campaign Details page.

![Add Campaign form](../../assets/campaign_add.png)
> The "Add Campaign" form.

## Campaign Details View

This is the control center for your campaign.
![Campaign details view](../../assets/campaign_detail.png)
> Campaign Details page showing Information, Files, and Tests sections.

### 1. Information
Displays the metadata of the campaign. You can edit or delete the campaign from here.

### 2. Files Management
This section allows you to manage files associated with the campaign (e.g., data files for tests, uploaded resources).
*   **Upload**: Add files to the campaign's working directory.
*   **Rename/Delete**: Manage existing files.
*   **Download**: Retrieve files.

These files are accessible in your tests using the `{{test.files_dir}}` variable.

### 3. Generated Reports
This section lists all reports (HTML, PDF, etc.) that have been generated from this campaign's executions.
*   **View**: See the type, date, and size of each report.
*   **Download**: Retrieve the report file.
*   **Delete**: Remove old reports.
*   **Refresh**: Update the list of available reports.

### 4. Tests List
Shows all tests in the campaign.
*   **Reorder**: Use the Up/Down arrows to change the execution order.
*   **Add Test**: Create a new test case.
*   **Execute**: Run a specific test individually.

## Executing a Campaign

1.  Click the **Execute Campaign** button.
2.  **Configure Execution**:
    *   **Name**: Auto-generated (e.g., "March 2023"), but customizable.
    *   **Environment**: Select the target environment (defined in Variables).
    *   **Stop on Failure**: If checked, the campaign stops immediately if a test fails.
3.  **Launch**: The execution runs in the background.

![Execute Campaign modal](../../assets/campaign_rapport.png)
> The "Execute Campaign" modal with environment selection.

### Real-time Monitoring
You will see a progress bar and status updates.
*   **Blue**: Running
*   **Green**: Completed Successfully
*   **Red**: Failed

Click on a running or completed report to view detailed logs.

## Plugin Data Structures

Plugin Data Structures allow you to save reusable configurations for action plugins. This is particularly useful for storing connection credentials (WebDAV, FTP, S3, SSH, etc.) that you use frequently across multiple tests.

### Concept

Some action plugins (WebDAV, FTP, SFTP, S3, SSH) provide a `get_structure()` function that defines the configurable fields for that plugin. For example, a WebDAV plugin might define:

| Field | Type | Description |
|-------|------|-------------|
| url | string | WebDAV server URL |
| username | string | Username |
| password | password | Password (obfuscated) |

### Creating a Data Structure

1. On the Campaign Details page, find the **Plugin Data Structures** section.
2. Click **Add data structure**.
3. Select a **Plugin type** from the dropdown (only plugins supporting data structures are listed).
4. Enter a **Structure name** (e.g., "Production WebDAV Server").
5. Fill in the **values** for each field.
6. Click **Save**.

### Managing Data Structures

The Plugin Data Structures section displays all saved configurations with:

| Column | Description |
|--------|-------------|
| Name | The unique name you gave the structure |
| Plugin type | The type of action plugin (shown as a colored badge) |
| Created | Creation date |
| Actions | View, Edit, or Delete buttons |

#### Available Actions:
*   **View** (👁): Opens a modal showing the structure's stored values (passwords are obfuscated).
*   **Edit** (✏️): Modify the name or values of the structure.
*   **Delete** (🗑): Remove the structure (with confirmation).

### Use Cases

1. **Centralized Credentials**: Store WebDAV, FTP, or S3 credentials once and reference them in multiple tests.
2. **Environment Switching**: Create separate structures for "Development", "Staging", and "Production" environments.
3. **Team Collaboration**: Share consistent configurations across team members through campaign export/import.

### Export and Import

Plugin Data Structures are automatically included when you export a campaign. When importing a campaign, all structures are restored with their original values.

!!! note "Security Note"
    Passwords and sensitive data marked with `obfuscate: true` are stored in the database but displayed as `••••••••` in the interface. Be careful when exporting campaigns as the actual values are included in the JSON file.

