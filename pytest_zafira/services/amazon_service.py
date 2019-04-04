import boto3
import logging
import base64

from pytest_zafira.utils.context import Context
from pytest_zafira.constants import PARAMETER


class AmazoneCloudService:
    """
    Uses for working with s3
    """
    logger = logging.getLogger('zafira')

    def __init__(self):
        self.aws_access_key = Context.get(PARAMETER['AWS_ACCESS_KEY'])
        self.aws_secret_access_key = Context.get(PARAMETER['AWS_SECRET_KEY'])
        self.bucket = Context.get(PARAMETER['AWS_SCREEN_SHOT_BUCKET'])

    def generate_amazon_presigned_URL(self, key, expires_in=86400):
        """
        :param key: Key to recognize file in bucket
        :param expires_in: Presigned URL expires in following number of seconds
        :return: Presigned URL to image
        """
        url = self.get_aws_s3_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket,
                    'Key': key},
            ExpiresIn=expires_in
        )
        self.logger.debug('Presigned URL to image:' + url)
        return url

    def upload_image_from_base64(self, base64_string, key, acl='private'):
        """
        Upload byte array from local machine to s3 storage
        :param base64_string: Image into base64 string format
        :param key: Key to recognize file in bucket
        :param acl: access to file. 'Private' by default
        """
        dec = base64.b64decode(base64_string)
        self.get_aws_s3_resource().Bucket(self.bucket).put_object(
            Key=key,
            Body=dec,
            ContentEncoding='base64',
            ContentType='image/png', ACL=acl
        )
        self.logger.debug('File was uploaded to S3')

    def get_aws_s3_client(self):
        """
        :return: client
        """
        return boto3.client('s3', aws_access_key_id=self.aws_access_key,
                            aws_secret_access_key=self.aws_secret_access_key)

    def get_aws_s3_resource(self):
        """
        Return aws s3 resource
        :return: resource
        """
        return boto3.resource('s3', aws_access_key_id=self.aws_access_key,
                              aws_secret_access_key=self.aws_secret_access_key)


amazon_cloud_service = AmazoneCloudService()
