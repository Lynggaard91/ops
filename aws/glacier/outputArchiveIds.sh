#!/usr/bin/env bash

# Source https://gist.github.com/veuncent/ac21ae8131f24d3971a621fac0d95be5
# Retrieve output from the retrieval job. Job ID from either initiation or the list job script is needed.

ACCOUNT_ID=""
REGION=""
VAULT_NAME=""
AWS_PROFILE=""
JOB_ID=""

aws glacier get-job-output --no-cli-pager --region "${REGION}" --account-id "${ACCOUNT_ID}" --profile "${AWS_PROFILE}" --vault-name "${VAULT_NAME}" --job-id="${JOB_ID}" ./output.json
