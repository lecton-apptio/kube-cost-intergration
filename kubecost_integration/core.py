"""Core functionality for Cloudability Kubernetes cost tracking."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class NamespaceCost:
    """Cost information for a Kubernetes namespace."""

    namespace: str
    start_date: str
    end_date: str
    total_cost: float
    currency: str = "USD"
    row_count: int = 0
    breakdown: Optional[list[dict[str, Any]]] = None

    def __post_init__(self) -> None:
        """Initialize breakdown if not provided."""
        if self.breakdown is None:
            self.breakdown = []


@dataclass
class CostBreakdown:
    """Detailed cost breakdown by service."""

    lease_type: str
    service_name: str
    transaction_type: str
    usage_family: str
    cost: float
    item_count: int


def load_env_file(path: str = ".env") -> None:
    """Load environment variables from a .env file.

    Args:
        path: Path to the .env file
    """
    import os

    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def redact_token(value: Optional[str]) -> Optional[str]:
    """Redact a token value for safe display.

    Args:
        value: The token value to redact

    Returns:
        Redacted version showing only first and last 4 characters
    """
    if not value:
        return value
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def build_curl_command(url: str, headers: dict[str, str], params: dict[str, Any]) -> str:
    """Build a curl command with redacted secrets.

    Args:
        url: The URL to request
        headers: HTTP headers to include
        params: Query parameters

    Returns:
        A formatted curl command string
    """
    # Build query string
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            for item in value:
                query_parts.append(f"{key}={item}")
        else:
            query_parts.append(f"{key}={value}")
    
    full_url = f"{url}?{'&'.join(query_parts)}" if query_parts else url
    
    parts = ["curl -sS -X GET", f'"{full_url}"']
    for key, value in headers.items():
        redacted_value = redact_token(value) if "token" in key.lower() else value
        parts.append(f'-H "{key}: {redacted_value}"')
    return " \\\n  ".join(parts)


def request_json(
    url: str, headers: dict[str, str], params: dict[str, Any], timeout: int = 30
) -> tuple[int, Any]:
    """Make an HTTP request and parse JSON response.

    Args:
        url: The URL to request
        headers: HTTP headers to include
        params: Query parameters
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, parsed_json_data)
    """
    # Build query string
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            for item in value:
                query_parts.append(f"{key}={item}")
        else:
            query_parts.append(f"{key}={value}")
    
    full_url = f"{url}?{'&'.join(query_parts)}" if query_parts else url
    
    request = Request(full_url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


class CloudabilityClient:
    """Client for Cloudability TrueCost Explorer API.

    This client uses Apptio OpenToken authentication to access Cloudability's
    cost reporting endpoints for Kubernetes namespace cost tracking.
    """

    def __init__(
        self,
        apptio_opentoken: str,
        environment_id: str,
        api_url: str = "https://api.cloudability.com",
    ) -> None:
        """Initialize Cloudability client.

        Args:
            apptio_opentoken: Apptio OpenToken for authentication
            environment_id: Apptio environment ID
            api_url: Cloudability API base URL
        """
        self.apptio_opentoken = apptio_opentoken
        self.environment_id = environment_id
        self.api_url = api_url

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers for API requests.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Accept": "*/*",
            "apptio-opentoken": self.apptio_opentoken,
            "apptio-environmentid": self.environment_id,
            "x-cldy-feature": "truecost_explorer",
        }

    def get_namespace_costs(
        self,
        namespace: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dimensions: Optional[list[str]] = None,
    ) -> NamespaceCost:
        """Get Kubernetes costs for a specific namespace.

        Args:
            namespace: Kubernetes namespace to filter by
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            dimensions: List of dimensions to group by

        Returns:
            NamespaceCost object with cost data

        Raises:
            HTTPError: If the API request fails
            URLError: If there's a network error
        """
        # Default dimensions
        if not dimensions:
            dimensions = [
                "lease_type",
                "enhanced_service_name",
                "transaction_type",
                "usage_family",
            ]

        # Default date range (last 30 days)
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start = datetime.now() - timedelta(days=30)
            start_date = start.strftime("%Y-%m-%d")

        # Build request parameters
        params: dict[str, Any] = {
            "filters": f"container_namespace=={namespace}",
            "metrics": "unblended_cost",
            "viewId": 0,
            "limit": 0,
            "offset": 0,
            "sort": "unblended_costDESC",
            "start": start_date,
            "end": end_date,
            "dimensions": dimensions,
        }

        # Make API request
        url = f"{self.api_url}/v3/internal/reporting/cost/run"
        headers = self._build_headers()

        try:
            status, data = request_json(url, headers, params)
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise HTTPError(
                e.url, e.code, f"Cloudability API error: {body}", e.hdrs, e.fp
            ) from e
        except URLError as e:
            raise URLError(f"Network error: {e.reason}") from e

        # Parse response
        aggregates = data.get("aggregates", [])
        total_cost = 0.0
        if aggregates and len(aggregates) > 0:
            values = aggregates[0].get("values", [])
            if values and len(values) > 0:
                total_cost = float(values[0])

        # Parse breakdown
        rows = data.get("rows", [])
        breakdown = []
        for row in rows:
            dims = row.get("dimensions", [])
            metrics = row.get("metrics", [{}])[0]
            cost_sum = float(metrics.get("sum", 0))
            count = int(metrics.get("count", 0))

            if len(dims) >= 4:
                breakdown.append(
                    {
                        "lease_type": dims[0],
                        "service_name": dims[1],
                        "transaction_type": dims[2],
                        "usage_family": dims[3],
                        "cost": cost_sum,
                        "item_count": count,
                    }
                )

        return NamespaceCost(
            namespace=namespace,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
            row_count=len(rows),
            breakdown=breakdown,
        )

    def get_config_summary(self) -> dict[str, Any]:
        """Get a summary of configured credentials.

        Returns:
            Dictionary with credential configuration status
        """
        return {
            "api_url": self.api_url,
            "environment_id": self.environment_id,
            "opentoken_present": bool(self.apptio_opentoken),
            "opentoken_redacted": redact_token(self.apptio_opentoken),
        }


# Made with Bob