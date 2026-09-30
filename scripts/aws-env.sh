#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAFFOLD_ENV="${SCRIPT_DIR}/../scaffold.env"

if [[ -f "${SCAFFOLD_ENV}" ]]; then
	# shellcheck disable=SC1091
	source "${SCAFFOLD_ENV}"
fi

export AWS_PROFILE="${AWS_PROFILE:-cornerstone}"
export AWS_REGION="${AWS_REGION:-us-east-2}"
export GITHUB_OWNER="${GITHUB_OWNER:-fourier-gauss-labs}"
export GITHUB_REPO="${GITHUB_REPO:-cornerstone}"
export ROLE_NAME="${AWS_ROLE_NAME:-github-actions-cornerstone-deploy}"