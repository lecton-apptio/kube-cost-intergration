"""Kubecost Integration Library.

A production-grade Python library for tracking Kubernetes costs via Cloudability's
TrueCost Explorer API.

Usage:
    from kubecost_integration import CloudabilityClient, NamespaceCost

    client = CloudabilityClient(
        apptio_opentoken="your-opentoken",
        environment_id="your-environment-id"
    )

    costs = client.get_namespace_costs(
        namespace="pythia",
        start_date="2026-05-15",
        end_date="2026-06-14"
    )

    print(f"Total cost: ${costs.total_cost:.2f}")
"""

from kubecost_integration.core import (
    CloudabilityClient,
    CostBreakdown,
    NamespaceCost,
    load_env_file,
    redact_token,
)

__version__ = "1.0.0"
__all__ = [
    "CloudabilityClient",
    "NamespaceCost",
    "CostBreakdown",
    "load_env_file",
    "redact_token",
]

# Made with Bob
