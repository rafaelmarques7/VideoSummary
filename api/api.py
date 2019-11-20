import flask
from gcs import gcs_file_exists
from google.cloud import storage
from urllib.parse import urlparse, parse_qs 


# constants
bucket_name = 'video_summary_bucket'

# GCS bucket handler
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)


# Function to extract query string parameters
def read_query_parameters(request):
  """This function extracts the query parameters: youtube_url, video_id"""
  youtube_url = None
  if request.args and 'youtube_url' in request.args:
    youtube_url = request.args.get('youtube_url') 
  return { 
    'youtube_url': youtube_url
    'video_id': extract_video_id_from_url(youtube_url)
  }


# Function to get video id from youtube url
def extract_video_id_from_url(url):
    video_id =  None
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    if 'v' in qs.keys() and len(qs['v']) >= 1: 
        video_id = qs['v'][0]
    return video_id    


# This is the GCF entrypoint - which implements the API
def main(request):
  # read and unpack query string parameters
  params = read_query_parameters(request)
  youtube_url, video_id = params['youtube_url'], params['video_id']
  # verify if video file exists in storage
  outfile_mp4 = youtube_id + '/audio.mp4'
  if gcs_file_exists(bucket, outfile_mp4):
    print('file exists')
  else: 
    print('file does not exist')
  return flask.jsonify({'statusCode': 200})    
