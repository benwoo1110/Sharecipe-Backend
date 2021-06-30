from os import name
import boto3


session = boto3.Session(
    aws_access_key_id="AKIAUUIALITO5Y5YY3NT",
    aws_secret_access_key="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",
)
s3_resource = session.resource('s3')


sharecipe_bucket = s3_resource.Bucket(name="sharecipe-storage")
sharecipe_bucket.upload_file(Filename="test.png", Key="test_bucket.png")
print("file uploaded!")


s3_resource.Object(bucket_name="sharecipe-storage", key="test_bucket.png").download_file('test_dowloaded.png')
print("file downloaded!")
