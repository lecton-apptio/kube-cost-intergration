# Kubecost Integration

A production-grade Python library for tracking Kubernetes costs via Cloudability's TrueCost Explorer API.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/lecton-apptio/kube-cost-intergration/actions/workflows/ci.yml/badge.svg)](https://github.com/lecton-apptio/kube-cost-intergration/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/lecton-apptio/kube-cost-intergration)

## Features

- 🔐 **Secure Authentication**: Uses Apptio OpenToken for long-lived sessions
- 📊 **Cost Tracking**: Get detailed Kubernetes namespace costs
- 🎯 **Type Safe**: Full type hints with `py.typed` marker
- ✅ **Well Tested**: 85%+ test coverage
- 📦 **Zero Dependencies**: Uses only Python standard library
- 🚀 **Production Ready**: Following best practices from enterprise integrations

## Installation

```bash
pip install kubecost-integration
```

## Quick Start

### Command Line

```bash
# Default: pythia namespace, last 30 days
python3 example.py

# Custom namespace
python3 example.py --namespace production

# Custom date range
python3 example.py --namespace pythia --start-date 2026-06-01 --end-date 2026-06-14

# Show help
python3 example.py --help
```

### Python API

```python
from kubecost_integration import CloudabilityClient

# Initialize client
client = CloudabilityClient(
    apptio_opentoken="your-opentoken-from-browser-cookies",
    environment_id="your-environment-id"
)

# Get namespace costs (defaults to last 30 days)
costs = client.get_namespace_costs(namespace="pythia")

# Or specify custom date range
costs = client.get_namespace_costs(
    namespace="production",
    start_date="2026-06-01",
    end_date="2026-06-14"
)

print(f"Total cost: ${costs.total_cost:.2f}")
print(f"Services: {costs.row_count}")

# Access detailed breakdown
for item in costs.breakdown:
    print(f"{item['service_name']}: ${item['cost']:.2f}")
```

## Authentication

### Getting Your OpenToken

The OpenToken is a session token from your browser cookies:

1. Open Cloudability in your browser (https://app.apptio.com/cloudability)
2. Open Developer Tools (F12)
3. Go to **Application** → **Cookies** → `https://app.apptio.com`
4. Find the `shell-opentoken` cookie
5. Copy its value (long hexadecimal string)

### Getting Your Environment ID

The Environment ID is also in your browser cookies:

1. In the same cookies view
2. Find the `envid` cookie
3. Copy its value (UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Using Environment Variables

Create a `.env` file:

```bash
APPTIO_OPENTOKEN=01ae074042d56d1d275dab7c383551120a10df82...
APPTIO_ENVIRONMENT_ID=dfa07190-0acb-4758-8d1b-a76fb6c6730e
```

Then in your code:

```python
import os
from kubecost_integration import CloudabilityClient, load_env_file

# Load .env file
load_env_file()

# Create client from environment
client = CloudabilityClient(
    apptio_opentoken=os.getenv("APPTIO_OPENTOKEN"),
    environment_id=os.getenv("APPTIO_ENVIRONMENT_ID")
)
```

## API Reference

### `CloudabilityClient`

Main client for interacting with Cloudability API.

#### `__init__(apptio_opentoken, environment_id, api_url="https://api.cloudability.com")`

Initialize the client.

**Parameters:**
- `apptio_opentoken` (str): Apptio OpenToken from browser cookies
- `environment_id` (str): Apptio environment ID
- `api_url` (str, optional): API base URL

#### `get_namespace_costs(namespace, start_date=None, end_date=None, dimensions=None)`

Get costs for a specific Kubernetes namespace.

**Parameters:**
- `namespace` (str): Kubernetes namespace name
- `start_date` (str, optional): Start date in YYYY-MM-DD format (default: 30 days ago)
- `end_date` (str, optional): End date in YYYY-MM-DD format (default: today)
- `dimensions` (list[str], optional): Cost dimensions to group by

**Returns:**
- `NamespaceCost`: Object containing cost data

**Example:**
```python
costs = client.get_namespace_costs(
    namespace="production",
    start_date="2026-05-01",
    end_date="2026-05-31"
)
```

### `NamespaceCost`

Dataclass containing namespace cost information.

**Attributes:**
- `namespace` (str): Namespace name
- `start_date` (str): Start date of cost period
- `end_date` (str): End date of cost period
- `total_cost` (float): Total cost for the period
- `currency` (str): Currency code (default: "USD")
- `row_count` (int): Number of cost breakdown rows
- `breakdown` (list[dict]): Detailed cost breakdown by service

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/lecton-apptio/kubecost-integration.git
cd kubecost-integration

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
black kubecost_integration tests

# Lint code
ruff check kubecost_integration tests

# Type check
mypy kubecost_integration
```

## Example Output

```
================================================================================
Namespace: pythia
Period: 2026-05-15 to 2026-06-14
Total Cost: $4.14 USD
Services: 7
================================================================================

Cost Breakdown:
--------------------------------------------------------------------------------
  On-Demand       | AWS EC2         | Usage      | Data Transfer        | $    1.36 (3012 items)
  Savings Plan    | AWS EC2         | Usage      | Instance Usage       | $    1.33 (43 items)
  On-Demand       | AWS EC2         | Usage      | Instance Usage       | $    1.30 (11 items)
  On-Demand       | AWS EBS         | Usage      | Provisioned IOPS     | $    0.13 (662 items)
  On-Demand       | AWS EBS         | Usage      | Storage              | $    0.04 (702 items)
--------------------------------------------------------------------------------
```

## Security

- **Never commit** your `.env` file or credentials to version control
- OpenToken expires after your browser session ends
- Tokens are automatically redacted in logs and error messages
- Use environment variables for production deployments

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Made with ❤️ by Bob**