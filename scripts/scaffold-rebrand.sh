#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_PATH="${REPO_ROOT}/scaffold.env"
DRY_RUN="false"
VERBOSE="false"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--dry-run] [--verbose]

Applies scaffold name replacements using values from scaffold.env.
By default this updates tracked text/config/code files and skips known runtime/build artifacts.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="true"
      ;;
    --verbose)
      VERBOSE="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "Missing scaffold config: ${CONFIG_PATH}" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${CONFIG_PATH}"

APP_SLUG="${APP_SLUG:-cornerstone}"
APP_DISPLAY_NAME="${APP_DISPLAY_NAME:-Cornerstone}"
API_NAME="${API_NAME:-cornerstone-api}"
API_VERSION="${API_VERSION:-0.1.0}"
AWS_ROLE_NAME="${AWS_ROLE_NAME:-github-actions-cornerstone-deploy}"

if [[ -z "${APP_SLUG}" || -z "${APP_DISPLAY_NAME}" || -z "${API_NAME}" ]]; then
  echo "APP_SLUG, APP_DISPLAY_NAME, and API_NAME must be set in scaffold.env" >&2
  exit 1
fi

esc() {
  perl -e 'print quotemeta($ARGV[0])' "$1"
}

is_in_scope() {
  local path="$1"

  case "$path" in
    *.md|*.txt|*.yml|*.yaml|*.toml|*.ini|*.env|*.py|*.sh|*.ts|*.tsx|*.json|*.svg|*.html|*.tf)
      ;;
    *)
      return 1
      ;;
  esac

  case "$path" in
    .git/*|.venv/*|node_modules/*|*/.venv/*|*/.terraform/*|*/node_modules/*)
      return 1
      ;;
  esac

  return 0
}

files=()
while IFS= read -r file; do
  if is_in_scope "$file" && [[ -f "${REPO_ROOT}/${file}" ]]; then
    files+=("${REPO_ROOT}/${file}")
  fi
done < <(cd "${REPO_ROOT}" && git ls-files)

src_cornerstone_api_esc="$(esc "cornerstone-api")"
src_cornerstone_display_esc="$(esc "Cornerstone")"
src_cornerstone_slug_esc="$(esc "cornerstone")"
src_role_esc="$(esc "github-actions-cornerstone-deploy")"
src_api_version_esc="$(esc "API_VERSION=0.1.0")"

dst_api_name_esc="$(esc "$API_NAME")"
dst_display_name_esc="$(esc "$APP_DISPLAY_NAME")"
dst_slug_esc="$(esc "$APP_SLUG")"
dst_role_esc="$(esc "$AWS_ROLE_NAME")"
dst_api_version_esc="$(esc "API_VERSION=$API_VERSION")"

replace_in_file() {
  local file="$1"
  local original_hash updated_hash

  if ! grep -Iq . "$file"; then
    return
  fi

  original_hash="$(sha256sum "$file" | awk '{print $1}')"

  perl -0pi -e "s/${src_cornerstone_api_esc}/${dst_api_name_esc}/g" "$file"
  perl -0pi -e "s/${src_cornerstone_display_esc}/${dst_display_name_esc}/g" "$file"
  perl -0pi -e "s/${src_cornerstone_slug_esc}/${dst_slug_esc}/g" "$file"
  perl -0pi -e "s/${src_role_esc}/${dst_role_esc}/g" "$file"
  perl -0pi -e "s/${src_api_version_esc}/${dst_api_version_esc}/g" "$file"

  updated_hash="$(sha256sum "$file" | awk '{print $1}')"

  if [[ "${original_hash}" != "${updated_hash}" ]]; then
    echo "${file#${REPO_ROOT}/}"
  fi
}

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "Dry run: files that would change"
  for file in "${files[@]}"; do
    tmp="$(mktemp)"
    cp "$file" "$tmp"
    changed="$(replace_in_file "$tmp" || true)"
    rm -f "$tmp"
    if [[ -n "$changed" ]]; then
      echo "${file#${REPO_ROOT}/}"
    fi
  done
  exit 0
fi

echo "Applying rebrand replacements from scaffold.env"
changed_count=0
for file in "${files[@]}"; do
  if [[ "${VERBOSE}" == "true" ]]; then
    echo "processing: ${file#${REPO_ROOT}/}"
  fi
  changed="$(replace_in_file "$file" || true)"
  if [[ -n "$changed" ]]; then
    echo "updated: $changed"
    changed_count=$((changed_count + 1))
  fi
done

echo "Done. Updated ${changed_count} tracked files."
