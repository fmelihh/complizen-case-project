import os
import boto3
from loguru import logger
from typing import Generator
from botocore.client import Config
from botocore.client import ClientError


class MinioFileStorage:
    def __init__(self):
        self._minio_client = None
        self._created_buckets = set()

    @property
    def minio_client(self) -> boto3.client:
        if self._minio_client is None:
            self._minio_client = boto3.client(
                "s3",
                endpoint_url=os.getenv("MINIO_ENDPOINT_URL", "http://0.0.0.0:9000"),
                aws_access_key_id=os.getenv(
                    "MINIO_ACCESS_KEY_ID", "HoEALUjdVOQpyUo8tF0X"
                ),
                aws_secret_access_key=os.getenv(
                    "MINIO_SECRET_ACCESS_KEY",
                    "NvotOjyK3zkeLXy8O3Lnf2SjgWtVAFIni2xL9809",
                ),
                config=Config(signature_version="s3v4"),
            )
        return self._minio_client

    def _create_bucket(self, bucket_name: str):
        if bucket_name in self._created_buckets:
            return

        try:
            self.minio_client.head_bucket(Bucket=bucket_name)
            self._created_buckets.add(bucket_name)
        except ClientError as e:
            logger.error(e)
            logger.info(f"{bucket_name} is not exists. It will be created.")
            self.minio_client.create_bucket(Bucket=bucket_name)

    def upload_file(
        self,
        bucket_name: str,
        filename: str,
        file_bytes: bytes,
        file_content_type: str,
    ) -> str:
        self._create_bucket(bucket_name=bucket_name)
        self.minio_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file_bytes,
            ContentType=file_content_type,
        )

    def is_exist(self, bucket_name: str, file_name: str) -> bool:
        self._create_bucket(bucket_name=bucket_name)
        try:
            self.minio_client.head_object(Bucket=bucket_name, Key=file_name)
            return True
        except ClientError as e:
            return False

    def get_file(self, bucket_name: str, file_name: str) -> bytes:
        self._create_bucket(bucket_name=bucket_name)
        try:
            response = self.minio_client.get_object(Bucket=bucket_name, Key=file_name)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to retrieve file '{file_name}': {e}")
            raise FileNotFoundError(
                f"File '{file_name}' not found in bucket '{bucket_name}'."
            )

    def list_file_keys(
        self, bucket_name: str, prefix: str = ""
    ) -> Generator[list[str], None, None]:
        self._create_bucket(bucket_name=bucket_name)
        continuation_token = None

        while True:
            list_kwargs = {"Bucket": bucket_name, "Prefix": prefix, "MaxKeys": 300}

            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token

            response = self.minio_client.list_objects_v2(**list_kwargs)
            contents = response.get("Contents", [])
            for obj in contents:
                yield obj["Key"]

            if not response.get("IsTruncated"):
                break

            continuation_token = response.get("NextContinuationToken")
