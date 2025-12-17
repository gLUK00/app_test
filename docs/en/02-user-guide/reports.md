# Reports and Monitoring

Reports provide a detailed history of campaign executions.

## Accessing Reports

*   **From Dashboard**: The "Reports" tab (if available) or via the Campaign Details page.
*   **From Campaign**: The "Reports" section lists all executions for that campaign.

## Report Details

Clicking on a report opens the detailed view:
![Report details](../../assets/campaign_rapport.png)
> Report details page showing the status header and the list of executed tests with their status icons.

### Header
*   **Status**: Success, Failure, or Running.
*   **Progress**: Percentage of completion.
*   **Environment**: The environment used for execution.
*   **Timings**: Start time, End time, and Total Duration.

### Test Results
A list of all tests executed in the campaign.
*   **Status Icon**: ✅ Pass / ❌ Fail.
*   **Logs**: Click to expand detailed execution logs.
    *   See exactly what data was sent and received.
    *   View execution time for each action.
    *   See error messages if an action failed.

## Real-time Updates
Reports use WebSockets to update in real-time. You don't need to refresh the page to see the progress of a running campaign.

## Generating Reports

You can generate exportable reports (PDF, HTML, etc.) from execution results.

1.  In the **General information** section, click the **Generate report** button.
2.  A modal window opens. Select the desired **Report Type** (e.g., HTML, PDF).
3.  Fill in the configuration fields specific to the chosen report (title, display options, etc.).
4.  Click **Generate**.
5.  Once the report is generated, a download link will appear.
