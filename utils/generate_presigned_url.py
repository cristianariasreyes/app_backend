import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError


def generate_presigned_url(file_name):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        s3_file_path = f"{settings.ENVIRONMENT_CUSTOM}/{file_name}"
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": s3_file_path},
            ExpiresIn=600,
        )  # 600 segundos = 10 minutos
    except NoCredentialsError:
        return None

    return response
