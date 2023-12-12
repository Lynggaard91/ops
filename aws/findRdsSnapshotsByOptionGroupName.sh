#!/usr/bin/env bash

#Change OPTIONGROUPNAME
jq '.DBSnapshots[] | select(.OptionGroupName=="OPTIONGROUPNAME") | {snapshot_id: .DBSnapshotIdentifier, instance: .DBInstanceIdentifier, OptionNameGroup: .OptionGroupName}'