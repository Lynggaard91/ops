import os
import boto3
from datetime import datetime

def list_objects_created_on(logging_bucket, prefix, date):
    s3 = boto3.client('s3')

    # Set the prefix and start after date
    list_kwargs = {'Bucket': logging_bucket, 'Prefix': prefix, 'StartAfter': f"{prefix}{date}/"}

    response = s3.list_objects_v2(**list_kwargs)
    objects = response.get('Contents', [])

    return objects

def download_objects(logging_bucket, objects, local_directory):
    s3 = boto3.client('s3')

    for obj in objects:
        key = obj['Key']
        local_path = os.path.join(local_directory, key)
        if not os.path.exists(local_path):
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(logging_bucket, key, local_path)
            print(f"Downloaded {key} to {local_path}")
        else:
            print(f"File {key} already exists locally, skipping download.")

def parse_log_file(file_path):
    bucket_access = {}

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            bucket_name = parts[1]  # Extracting the bucket name from the second part
            if bucket_name.startswith('cet-'):
                bucket_name = bucket_name[len('cet-'):]  # Removing the 'cet-' prefix
                if bucket_name not in bucket_access:
                    bucket_access[bucket_name] = {}

                user_arn = parts[5]
                operation = parts[7]

                if user_arn not in bucket_access[bucket_name]:
                    bucket_access[bucket_name][user_arn] = {}

                if operation not in bucket_access[bucket_name][user_arn]:
                    bucket_access[bucket_name][user_arn][operation] = 0

                bucket_access[bucket_name][user_arn][operation] += 1

    return bucket_access

def summarize_access(bucket_access):
    summary = {}
    for bucket, access_info in bucket_access.items():
        summary[bucket] = {}
        for user, operations in access_info.items():
            summary[bucket][user] = {
                'total_operations': sum(operations.values()),
                'operations': operations
            }
    return summary

if __name__ == "__main__":
    logging_bucket = input("Enter the S3 logging bucket name: ")
    prefix = input("Enter the prefix to filter objects (e.g., 'log/'): ")
    date = input("Enter the date to filter objects (format: YYYY-MM-DD): ")
    local_directory = input("Enter the local directory to store downloaded files: ")

    objects = list_objects_created_on(logging_bucket, prefix, date)
    download_objects(logging_bucket, objects, local_directory)

    bucket_access = {}
    for obj in objects:
        key = obj['Key']
        file_path = os.path.join(local_directory, key)
        bucket_access.update(parse_log_file(file_path))

    summary = summarize_access(bucket_access)

    print("Summary of bucket access:")
    for bucket, access_info in summary.items():
        print(f"\nBucket: {bucket}")
        for user, info in access_info.items():
            print(f"  User: {user}")
            print(f"    Total Operations: {info['total_operations']}")
            print("    Operations:")
            for operation, count in info['operations'].items():
                print(f"      {operation}: {count}")
