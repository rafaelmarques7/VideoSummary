from pytube import YouTube

# Function to download youtube video. Stores video in GCS.
def get_youtube_video(yt_link, output_filename):
    yt_object = YouTube(yt_link)
    yt_stream = yt_object.streams.filter(only_audio=True).first()
    data = yt_stream.stream_to_buffer()
    with GCSObjectStreamUpload(client=storage_client, bucket_name=bucket_name, blob_name=output_filename) as fh:
        fh.write(data.getbuffer())

