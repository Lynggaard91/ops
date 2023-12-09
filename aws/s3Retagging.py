import logging
import boto3
import re
from ast import literal_eval

# vars
s3_bucket_name = 'S3BUCKETNAME'
session = boto3.Session(profile_name='<AWSPROFILE>')
tagset = {}
cleanup_regex = '''{'Key':\s'TAGKEY',\s'Value':\s'TAGVALUE'}'''
awsrequests = 0

# Set S3 Client & Resource

s3_resource = session.resource('s3')
s3_client = session.client('s3')
bucket = s3_resource.Bucket(s3_bucket_name)

# Logging configuration
logging.basicConfig(filename='retagging.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',)


# Functions

# fetches tags (tagset) on objects


def check_tags(bucket_name, key_prefix):
    tags = s3_client.get_object_tagging(
        Bucket=bucket_name,
        Key=key_prefix,
    )
    return tags

# cleanup_tag replaces a tagset as a whole (all tags) for an given object


def cleanup_tag(bucket_name, s3_object_key, storageclass, archive=False):

    # archive_tag & storageclass_cleanup_tag will be used to replace a schedule tag, such as {'Key': 'daily','Value': 'true'}

    archive_tag = {
        'Key': 'archive',
        'Value': 'true'}

    storageclass_cleanup_tag = {
        'Key': 'cleanup',
        'Value': storageclass}

    # cleanup_method_tag sets the tag to be used in the conditional logic to come.
    cleanup_method_tag = storageclass_cleanup_tag

    try:

        # Retrieve tags of S3 object.
        obj_tags = check_tags(
            bucket_name, s3_object_key)

        # Store its tagset into tagset var.
        tagset = obj_tags['TagSet']

        # Based on the regex above under Environments, find schedule tags that's called either "daily", "weekly" or "monthly".
        findscheduletags = re.search(
            cleanup_regex, str(tagset), re.IGNORECASE)

        # Failsafe in case no matches are found for the current object.
        if findscheduletags is None:
            logging.info(
                "Did not find any matching tagset for " + str(s3_object_key))

        else:

            # If archive argument is set then apply archivation logic, this will make sure to set the archivation tag.
            if archive == True:

                # Below regex helps figuring out whether or not to archive an object.
                findmonthly = re.findall('monthly', findscheduletags.group(0))
                if 'monthly' in findmonthly:
                    cleanup_method_tag = archive_tag

            # Below regex will be used to avoid overwriting an already archived object.
            findarchive = re.findall('archive', findscheduletags.group(0))

            # Finishes the function if the object already has an archive tag.
            if 'archive' in findarchive:
                logging.warning(
                    "Object already filed for archivation " + str(s3_object_key))
                return None

            # Remove the schedule tag 'daily', 'weekly' or 'monthly'.
            for i in range(len(tagset)):
                if tagset[i]['Key'] == literal_eval(findscheduletags.group(0))['Key']:
                    del tagset[i]
                    break

            logging.info("Removed tag from " + str(findscheduletags.group(0)))

            # Add the new tag to the tagset list (list of dicts)
            tagset.append(cleanup_method_tag)
            tagset = {'TagSet': tagset}

            # Override the current tags - this does not append.
            s3_client.put_object_tagging(
                Bucket=bucket_name,
                Key=s3_object_key,
                Tagging=tagset
            )

            logging.info("Succesfully applied " + str(tagset) +
                         " to " + str(s3_object_key))

    except BaseException as err:
        logging.error(f"Unexpected {err=}, {type(err)=}")
        raise

# Set clean up tag for daily & weekly backup files, archive monthly reportmessages.

logging.info('**************** STARTING ****************')

# Store all S3 Bucket's objects into var
s3_objectlist = bucket.objects.all()
awsrequests = awsrequests + 1

# Iterate over all objects
for obj in s3_objectlist:

    # Find out whether or not the obj is a part of 'SOMESTRING', used for archivation of
    # backups that are scheduled for 'monthly' - we want to keep these forever (for now)
    findings = re.findall(r'\/SOMESTRING\/',
                          obj.key.lower(), re.IGNORECASE)

    # We need to use the client session in order to extract low-level information, in this
    # case storageclass
    client_obj = s3_client.list_objects_v2(
        Bucket=obj.bucket_name, Prefix=obj.key)

    storageclass = client_obj['Contents'][0]['StorageClass'].lower()

    awsrequests = awsrequests + 1

    # We're not interested in doing anything to objects that are fresh, so we'll skip objects
    # which are still standard storage (these will transition eventually).

    if storageclass == 'standard':
        logging.info(obj.key + " is standard storage, skipping..")
        continue

    else:

        # Perform archive logic to SOMESTRING Monthly backups
        if '/SOMESTRING/' in findings:

            cleanup_tag(obj.bucket_name, obj.key, storageclass, archive=True)
            awsrequests = awsrequests + 2

        # Perform standard cleanup tag logic to common backups.
        else:

            cleanup_tag(obj.bucket_name, obj.key, storageclass, archive=False)
            awsrequests = awsrequests + 2

logging.info("Total AWS Requests made " + str(awsrequests))