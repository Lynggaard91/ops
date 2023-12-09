#!/usr/bin/env bash

# Source https://gist.github.com/veuncent/ac21ae8131f24d3971a621fac0d95be5
# Initiate retrieval of archives from your Glacier Vault

ACCOUNT_ID=""
REGION=""
VAULT_NAME=""
AWS_PROFILE=""

aws glacier initiate-job --job-parameters '{"Type": "inventory-retrieval"}' --account-id "${ACCOUNT_ID}" --region "${REGION}" --vault-name "${VAULT_NAME}" --profile "${AWS_PROFILE}"
