# Reports and Monitoring

Reports provide a detailed history of campaign executions.

## Accessing Reports

*   **From Dashboard**: The "Reports" tab (if available) or via the Campaign Details page.
*   **From Campaign**: The "Reports" section lists all executions for that campaign.

## Report Details

Clicking on a report opens the detailed view:

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
