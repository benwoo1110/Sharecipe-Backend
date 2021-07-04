import os
from os import path
import re
import uuid
import boto3
import config


SAVE_LOCATION = './downloads'


class S3FileManager:
    def __init__(self) -> None:
        if not path.isdir(SAVE_LOCATION):
            os.mkdir(SAVE_LOCATION)

        session = boto3.Session(aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
        self.s3_resource = session.resource('s3')

    def get_local_path(self, file_id):
        return path.join(SAVE_LOCATION,  str(file_id))

    def save(self, file_received):
        file_id = str(uuid.uuid1())
        file_received.save(self.get_local_path(file_id))
        self.upload(file_id)
        return file_id

    def upload(self, file_id):
        self.s3_resource.Bucket(config.AWS_BUCKET_NAME).upload_file(Filename=self.get_local_path(file_id), Key=file_id)

    def download(self, file_id):
        output = self.get_local_path(file_id)
        if path.isfile(output):
            return output
        
        self.s3_resource.Bucket(config.AWS_BUCKET_NAME).download_file(file_id, output)
        return output


    def delete(self, file_id):
        cached = self.get_local_path(file_id)
        if path.isfile(cached):
            os.remove(cached)

        self.s3_resource.Object(config.AWS_BUCKET_NAME, file_id).delete()


class LocalFileManager:
    def __init__(self) -> None:
        if not path.isdir(SAVE_LOCATION):
            os.mkdir(SAVE_LOCATION)

    def get_local_path(self, file_id):
        return path.join(SAVE_LOCATION,  str(file_id))

    def save(self, file_received):
        file_id = str(uuid.uuid1())
        file_received.save(self.get_local_path(file_id))
        return file_id

    def upload(self, file_id):
        pass

    def download(self, file_id):
        output = self.get_local_path(file_id)
        return output

    def delete(self, file_id):
        cached = self.get_local_path(file_id)
        if path.isfile(cached):
            os.remove(cached)
