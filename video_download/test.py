from pytube import YouTube

yt_link='https://www.youtube.com/watch?v=9_-wndK57Ls'

# Function to download youtube video. Stores video in GCS.
def get_youtube_video():
    yt_object = YouTube(yt_link)
    # yt_stream = yt_object.streams.filter(only_audio=True).first()
    # yt_stream = yt_object.streams.filter(progressive=True).first()
    yt_stream = yt_object.streams.filter(progressive=True).order_by('resolution').desc().first()
    yt_stream.download()
    print('done')

get_youtube_video()