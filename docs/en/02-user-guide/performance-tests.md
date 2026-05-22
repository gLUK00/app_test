# Performance Tests

Performance tests allow you to run one or more existing tests multiple times (instances) and measure response times as well as success rates.

## Launching a Performance Test

From a campaign page, in the **Execution Reports** section, click the **Performance Test** button (orange, to the right of the "Run Campaign" button).

You will be taken to the performance test configuration page.

## Configuration

### Global Configuration

| Field | Description |
|-------|-------------|
| **Environment (tier)** | Select the target environment (e.g., `dev`, `staging`, `prod`). |
| **Run tests in parallel** | If enabled, different tests will be launched simultaneously. |
| **Number of parallel tests** | (Visible if parallel is enabled) Maximum number of tests running at the same time. |

### Per-test Configuration

For each test in the campaign, you can configure:

| Field | Description |
|-------|-------------|
| **Include** | Check/uncheck to include or exclude the test from the performance test. |
| **Number of instances** | How many times the test will be executed (e.g., `100` means 100 runs). |
| **Run instances in parallel** | (Visible if instances > 1) The test instances execute in parallel. |
| **Parallel instances** | (Visible if parallel is enabled) Maximum number of simultaneous instances. |
| **Stop on first instance failure** | (Visible if instances > 1) Stops execution when an instance fails. |

## Launch and Real-time Monitoring

Click **Launch performance test** to start. You are automatically redirected to the **Performance Dashboard** which displays:

- A **global progress bar** updated in real-time (WebSocket)
- An animated red **LIVE** indicator during execution
- **Global statistics**:
  - Generated / executed / passed / failed instances
  - Average, minimum, maximum, and total execution time
- **Per-test cards** with the same metrics and an individual progress bar

## Results

Once the test is complete:
- The final status is displayed (success or failures)
- The report is saved and visible in the campaign's execution reports list with an orange **PERF** badge
- Clicking the badge or report opens the corresponding performance dashboard directly

## Performance Reports in the List

Performance reports appear in the execution reports list with an orange `PERF` badge. The report name is automatically generated as `Perf - Month Year` (e.g., `Perf - July 2026`).

## Variable Isolation

Each test instance runs in an isolated variable context. Variables modified by one instance do not affect other instances.
