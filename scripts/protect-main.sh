#!/usr/bin/env bash
# Require the PR checks + 1 approval before merging to main. Usage: scripts/protect-main.sh owner/repo
set -euo pipefail
REPO=${1:?usage: protect-main.sh owner/repo}

gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["pr-checks"] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 1 },
  "restrictions": null
}
JSON
