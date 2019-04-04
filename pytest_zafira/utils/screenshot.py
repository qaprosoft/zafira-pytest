import random
import uuid
from datetime import date
import logging
import string

from pytest_zafira.services import amazon_cloud_service
from pytest_zafira.utils.context import Context
from pytest_zafira.constants import PARAMETER
from pytest_zafira import ZafiraListener


class Screenshot:

    AMAZON_KEY_FORMAT = 'artifacts/screenshots/{}/'
    DATE_FORMAT = '%m-%d-%Y'

    logger = logging.getLogger('zafira')

    @classmethod
    def upload_to_amazon_S3(cls, file):
        if not Context.get(PARAMETER['S3_SAVE_SCREENSHOTS']):
            cls.logger.debug(
                "there is no sense to continue as saving"
                " screenshots onto S3 is disabled."
            )
            return

        correlation_id = str(uuid.uuid4())
        test_id = ZafiraListener().ci_test_id
        expires_in = Context.get(
            PARAMETER['ARTIFACT_EXPIRES_IN_DEFAULT_TIME']
        )

        filename = ''.join(
            random.sample((string.ascii_lowercase + string.digits), 10)
        ) + '.png'

        key = cls.AMAZON_KEY_FORMAT.format(
            str(date.today().strftime(cls.DATE_FORMAT))
        ) + filename

        logging.getLogger('zafira').info("TEST FAILED!")
        logging.getLogger('zafira').setLevel('META_INFO')
        logging.getLogger('zafira').meta_info(
            "Uploading to AWS: {}. Expires in {} seconds.".format(filename,
                                                                  expires_in),
            extra={'amazon_path': None,
                   'test_id': test_id,
                   'correlation_id': correlation_id}
        )
        amazon_cloud_service.upload_image_from_base64(file, key)

        url = amazon_cloud_service.generate_amazon_presigned_URL(
            key,
            expires_in=expires_in
        )

        logging.getLogger('zafira').meta_info(
            "Uploaded to AWS: " + filename,
            extra={'amazon_path': url,
                   'test_id': test_id,
                   'correlation_id': correlation_id})

        logging.getLogger('zafira').setLevel(logging.INFO)
