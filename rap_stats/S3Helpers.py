## AWS S3 HELPER FUNCTIONS
import boto3
import botocore
import json
from os import environ



#enviornment setup

_bucket_name = ''
_resource = None
_client = None

if 'SERVERTYPE' in environ and environ['SERVERTYPE'] == 'AWS Lambda':
	_resource = boto3.resource('s3')
    _client = boto3.client('s3')
	_bucket_name = environ.get('DATA-BUCKET')

else:
    from . import Config
	_resource = boto3.resource('s3',
		aws_access_key_id=Config.AWSAccessKeyId,
		aws_secret_access_key=Config.AWSSecretKey
		)
	_bucket_name = 'rap-stats-data'


bucket = _resource.Bucket(BUCKET_NAME)


## public funcions 
get_json = lambda f: json.load(bucket.Object(key=f).get()["Body"])
put_json = lambda obj, f: bucket.Object(key=f).put(Body=json.dumps(obj))
del_obj = lambda f: _client.delete_object(Bucket=_bucket_name, Key=f)
client_error = botocore.exceptions.ClientError


def exp_backoff_with_jitter(exception=Exception, max_sleep=60, base=0.001, max_retries=100):
    def arg_decorator(func):
        @wraps(func)
        def func_wrap(*args, **kwargs):
            for attempt in range(max_retries):

                try:
                    return func(*args, **kwargs)

                except exception as e:
                    pass

                sleep_time = rand.uniform(0, min(max_sleep, base * 2 ** attempt))
            print('returning none')
            return None
        return func_wrap
    return arg_decorator












def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    kwargs = {'Bucket': BUCKET_NAME}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3_resource.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
	




