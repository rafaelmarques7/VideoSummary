import flask
from logic.gcs import gcs_file_exists
from google.cloud import storage
from urllib.parse import urlparse, parse_qs

# Constants
BUCKET_NAME = 'video_summary_bucket'
CODE_SUCCESS = 200
CODE_USER_ERROR = 400
CODE_INTERNAL_ERROR = 500
SUMMARY_RATIO_DEFAULT = 0.3

# GCS bucket handler
storage_client = storage.Client()
bucket = storage_client.get_bucket(BUCKET_NAME)


# Function to extract query string parameters
def read_query_parameters(request):
    """This function extracts the query parameters: youtube_url, youtube_id"""
    # default values
    youtube_url = None
    summary_ratio = SUMMARY_RATIO_DEFAULT
    # extract youtube_url
    if request.args and 'youtube_url' in request.args:
        youtube_url = request.args.get('youtube_url')
    # extract summary_ratio
    if request.args and 'summary_ratio' in request.args:
        try:
            ratio = float(request.args.get('summary_ratio'))
            if ratio >= 0.1 and ratio <= 0.9:
                summary_ratio = ratio
        except:
            print('summary_ratio provided can not be converted to float. using default ratio.')
    # return all parameters
    return {
        'youtube_url': youtube_url,
        'youtube_id': extract_youtube_id_from_url(youtube_url),
        'summary_ratio': summary_ratio,
    }


# Function to get video id from youtube url
def extract_youtube_id_from_url(url):
    youtube_id = None
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    if 'v' in qs.keys() and len(qs['v']) >= 1:
        youtube_id = qs['v'][0]
    return youtube_id


# Helper function to return a response with status code and CORS headers
def prepare_response(res_object, status_code):
    response = flask.jsonify(res_object)
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST')
    return response, status_code


# This is the GCF entrypoint - which implements the API
def main(request):
    # Read and unpack query string parameters
    params = read_query_parameters(request)
    youtube_url, youtube_id, summary_ratio = params['youtube_url'], params['youtube_id'], params['summary_ratio']
    # Handle bad user input 
    if not youtube_url or not youtube_id:
        res = { 'error': 'You must provide a valid youtube_url as query string parameter' }
        return prepare_response(res, CODE_USER_ERROR)
    # Call f_youtube

