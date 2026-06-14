#!/usr/bin/env python3
"""Example usage of kubecost-integration library with CLI arguments."""

import argparse
import os
from datetime import datetime, timedelta

from kubecost_integration import CloudabilityClient, load_env_file

# Load environment variables from .env file
load_env_file()


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Get Kubernetes namespace costs from Cloudability"
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default="pythia",
        help="Kubernetes namespace (default: pythia)"
    )
    parser.add_argument(
        "--start-date",
        "-s",
        help="Start date in YYYY-MM-DD format (default: 30 days ago)"
    )
    parser.add_argument(
        "--end-date",
        "-e",
        help="End date in YYYY-MM-DD format (default: today)"
    )
    
    args = parser.parse_args()
    
    # Get credentials from environment
    opentoken = os.getenv("APPTIO_OPENTOKEN")
    env_id = os.getenv("APPTIO_ENVIRONMENT_ID")

    if not opentoken or not env_id:
        print("❌ ERROR: Missing credentials")
        print("Set APPTIO_OPENTOKEN and APPTIO_ENVIRONMENT_ID in .env file")
        exit(1)

    # Create client
    client = CloudabilityClient(
        apptio_opentoken=opentoken,
        environment_id=env_id
    )

    # Get namespace costs
    print(f"Fetching costs for namespace '{args.namespace}'...")
    if args.start_date and args.end_date:
        print(f"Date range: {args.start_date} to {args.end_date}")
    else:
        print("Date range: Last 30 days")
    
    costs = client.get_namespace_costs(
        namespace=args.namespace,
        start_date=args.start_date,
        end_date=args.end_date
    )

    # Display results
    print(f"\n{'='*80}")
    print(f"Namespace: {costs.namespace}")
    print(f"Period: {costs.start_date} to {costs.end_date}")
    print(f"Total Cost: ${costs.total_cost:.2f} {costs.currency}")
    print(f"Services: {costs.row_count}")
    print(f"{'='*80}\n")

    # Display breakdown
    if costs.breakdown:
        print("Cost Breakdown:")
        print(f"{'-'*80}")
        for item in costs.breakdown:
            print(
                f"  {item['lease_type']:15} | "
                f"{item['service_name']:15} | "
                f"{item['transaction_type']:10} | "
                f"{item['usage_family']:20} | "
                f"${item['cost']:8.2f} ({item['item_count']} items)"
            )
        print(f"{'-'*80}")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()

# Made with Bob
