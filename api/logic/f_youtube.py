from pytube import YouTube
from pydub import AudioSegment


# Function to download youtube video. Stores video in GCS using.
def get_youtube_video(yt_link, output_filename):
    print('inside get_youtube_video, youtube_link: ', yt_link)
    yt_object = YouTube(yt_link)
    # audio and video - this is faster than downloading just audio
    yt_stream = yt_object.streams.filter(progressive=True).first()
    data = yt_stream.stream_to_buffer()
    # download and stream data to GCS
    with GCSObjectStreamUpload(client=storage_client, bucket_name=bucket_name, blob_name=output_filename) as fh:
        fh.write(data.getbuffer())


# Function to transform .mp4 to .flac
def transform_audio_to_flac(input_filename, output_filename):
    print('inside transform_audio_to_flac')
    # constants for local storage
    local_filename = '/tmp/temp.mp4'
    local_filename_transformed = '/tmp/temp.flac'
    # Get file from GCS
    download_blob(input_filename, local_filename)
    # Convert file from MP4 to flac
    mp4_audio = AudioSegment.from_file(local_filename, format="mp4")
    mp4_audio.export(local_filename_transformed, format="flac")
    # Store file to GCS
    upload_blob(local_filename_transformed, output_filename)
