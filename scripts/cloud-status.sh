#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <aws|azure|gcp>"
  exit 1
fi

cloud="$1"

case "$cloud" in
  aws)
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Load the project-specific AWS profile and region.
    # aws-env.sh sets GITHUB_REPO, which is used as the resource name prefix.
    source "$script_dir/aws-env.sh"

    aws apprunner list-services \
      --query "ServiceSummaryList[?contains(ServiceName, '${GITHUB_REPO}-dev')].[ServiceName,Status,ServiceUrl]" \
      --output table
    ;;
  azure|gcp)
    echo "Cloud vendor $cloud not yet supported"
    ;;
  *)
    echo "No plans to suppout cloud vendor $cloud at this time"
    exit 1
    ;;
esac
