#!/usr/bin/env bash

# Source https://gist.github.com/veuncent/ac21ae8131f24d3971a621fac0d95be5
# Delete archives from Vault. Dependent on size this may take minutes, hours or days.

ACCOUNT_ID=""
REGION=""
VAULT_NAME=""
AWS_PROFILE=""

file='./output.json'
id_file='./output-archive-ids.txt'

if [[ -z ${AWS_ACCOUNT_ID} ]] || [[ -z ${AWS_REGION} ]] || [[ -z ${AWS_VAULT_NAME} ]]; then
        echo "Please set the following environment variables: "
        echo "AWS_ACCOUNT_ID"
        echo "AWS_REGION"
        echo "AWS_VAULT_NAME"
        exit 1
fi

echo "Started at $(date)"

echo -n "Getting archive ids from $file..."
if [[ ! -f $id_file ]]; then
  cat $file | jq -r --stream ". | { (.[0][2]): .[1]} | select(.ArchiveId) | .ArchiveId" > $id_file 2> /dev/null
fi
total=$(wc -l $id_file | awk '{print $1}')
echo "got $total"

num=0
while read -r archive_id; do
  num=$((num+1))
  echo "Deleting archive $num/$total at $(date)"
  aws glacier delete-archive --profile="${AWS_PROFILE}" --archive-id="${archive_id}" --vault-name "${VAULT_NAME}" --account-id "${ACCOUNT_ID}" --region "${REGION}" &
  [ $( jobs | wc -l ) -ge $( nproc ) ] && wait
done < "$id_file"

wait
echo "Finished at $(date)"
echo "Deleted archive ids are in $id_file"
