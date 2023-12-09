# If 'apply-immediately' was missed posting changes to RDS, this is a second chance. Careful though.
aws rds modify-db-instance --apply-immediately --db-instance-identifier <db-id>