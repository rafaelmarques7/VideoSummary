from google.cloud import storage
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums


bucket_name = 'video_summary_bucket'
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)


# Function to download from GCS
def download_blob(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    print('inside download_blob')
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print('File {} has been downloaded to {}.'.format(source_blob_name, destination_file_name))

download_blob("9_-wndK57Ls/audio.mp4", "./audio.mp4")
# download_blob("9_-wndK57Ls/audio.mp3")
