from app.core.config import config


def generate_presigned_url(media_url: str, s3_client):
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': config.BUCKET_NAME, 'Key': media_url},
        ExpiresIn=3600
    )
    return presigned_url    
