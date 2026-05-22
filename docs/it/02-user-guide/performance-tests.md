# Performance Tests

Performance tests allow you to run one or more existing tests multiple times (instances) and measure response times as well as success rates.

## Launching a Performance Test

From a campaign page, in the **Execution Reports** section, click the **Performance Test** button (orange, to the right of the "Run Campaign" button).

## Configuration

### Global Configuration

| Field | Description |
|-------|-------------|
| **Environment (tier)** | Select the target environment (e.g., `dev`, `staging`, `prod`). |
| **Run tests in parallel** | If enabled, different tests will be launched simultaneously. |
| **Number of parallel tests** | Maximum number of tests running at the same time. |

### Per-test Configuration

| Field | Description |
|-------|-------------|
| **Include** | Include or exclude the test from the performance test. |
| **Number of instances** | How many times the test will be executed. |
| **Run instances in parallel** | The test instances execute in parallel. |
| **Parallel instances** | Maximum number of simultaneous instances. |
| **Stop on first instance failure** | Stops execution when an instance fails. |

## Real-time Dashboard

After launching, the performance dashboard shows:
- Global progress bar (WebSocket real-time)
- Instance statistics (total, executed, passed, failed)
- Execution times (average, min, max, total)
- Per-test result cards

## Variable Isolation

Each test instance runs in an isolated variable context.
