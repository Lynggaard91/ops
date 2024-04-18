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
    parsed_logs = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            timestamp = parts[2][1:] + ' ' + parts[3][:-1]  # Concatenate date and time parts
            ip_address = parts[4]
            user_arn = parts[5]
            request_id = parts[6]
            operation = parts[7]
            object_key = parts[8].strip('"')
            status_code = parts[10]
            parsed_logs.append({
                'timestamp': timestamp,
                'ip_address': ip_address,
                'user_arn': user_arn,
                'request_id': request_id,
                'operation': operation,
                'object_key': object_key,
                'status_code': status_code
            })
    return parsed_logs

if __name__ == "__main__":
    logging_bucket = input("Enter the S3 logging bucket name: ")
    prefix = input("Enter the prefix to filter objects (e.g., 'log/'): ")
    date = input("Enter the date to filter objects (format: YYYY-MM-DD): ")
    local_directory = input("Enter the local directory to store downloaded files: ")

    objects = list_objects_created_on(logging_bucket, prefix, date)
    download_objects(logging_bucket, objects, local_directory)

    for obj in objects:
        key = obj['Key']
        file_path = os.path.join(local_directory, key)
        parsed_logs = parse_log_file(file_path)
        print(f"Logs from {key}:")
        for log in parsed_logs:
            print(log)
