import os
from os import path
import re
import uuid
import boto3
import config


SAVE_LOCATION = './downloads'
session = boto3.Session(aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
s3_resource = session.resource('s3')


if not path.isdir(SAVE_LOCATION):
    os.mkdir(SAVE_LOCATION)


def save(file_received):
    file_id = str(uuid.uuid1())
    file_received.save(path.join(SAVE_LOCATION,  str(file_id)))
    upload(file_id)
    return file_id


def upload(file_id):
    s3_resource.Bucket(config.AWS_BUCKET_NAME).upload_file(Filename=path.join(SAVE_LOCATION,  str(file_id)), Key=file_id)


def download(file_id):
    output = path.join(SAVE_LOCATION, file_id)
    s3_resource.Bucket(config.AWS_BUCKET_NAME).download_file(file_id, output)
    return output
