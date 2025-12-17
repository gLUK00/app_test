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
