import urllib.request
import subprocess
import boto3 
import os

s3 = boto3.client('s3')

def split_s3_uri_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def split_object_url_path(s3_path):
    path_parts=s3_path.replace("https://","").split("/")
    bucket=path_parts.pop(0).split(".").pop(0)
    key="/".join(path_parts)
    return bucket, key

def download_file(link, full_audio_path):
    print("Start downloading: {}".format(link))
    if link.startswith("https://s3"):
        # In Amazon S3, path-style URLs use the following format.
        # https://s3.Region.amazonaws.com/bucket-name/key-name
        urllib.request.urlretrieve(link, full_audio_path)
    elif link.startswith("https://"):
        # Object URL.
         bucket, key = split_object_url_path(link)
         s3.download_file(bucket, key, full_audio_path)
    elif link.startswith("s3://"):
         bucket, key = split_s3_uri_path(link)
         s3.download_file(bucket, key, full_audio_path)

if __name__ == "__main__":
    audio_folder = "data"
    links = ["https://s3-ap-southeast-1.amazonaws.com/carro.co/2022/05/Listing/36417109/toyota-vios-1.5-e-2013-GY7Y7Z-carro-001.", 
            "https://ds-acoustic-audioset.s3.ap-southeast-1.amazonaws.com/listing-10s-audio/toyota-vios-1_5-e-2013-GY7Y7Z-carro-001__20220523030203_147159.wav"]
    for link in links:
        file_name = link.split("/")[-1]
        full_audio_path = os.path.join(audio_folder, file_name)
        download_file(link, full_audio_path)