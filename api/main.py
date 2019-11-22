import flask
from google.cloud import storage
from urllib.parse import urlparse, parse_qs
from logic.gcs import gcs_file_exists
from logic.f_youtube import f_youtube
from constants import BUCKET_NAME, CODE_SUCCESS, \
    CODE_USER_ERROR, CODE_INTERNAL_ERROR, SUMMARY_RATIO_DEFAULT


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
    return {
        'youtube_url': youtube_url,
        'summary_ratio': summary_ratio,
    }


# Function to get video id from youtube url
def extract_video_id_from_url(url):
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    if 'v' in qs.keys() and len(qs['v']) >= 1: 
        video_id = qs['v'][0]
    else:
        video_id = None
    return video_id    


# Function to determine if video has been (fully) processed before
def check_video_has_been_processed(video_id):
    """ This function verifies if this video has been processed and all files are available in GCS"""
    # List of files that should be in GCS for this video to have been succesfully processed before
    # Note: we might remove the video and audio in the future, as we care more about transcript and summary.
    files_required = [
        f'{video_id}/video.mp4',
        f'{video_id}/audio.flac',
        f'{video_id}/metadata.json',
        f'{video_id}/transcript.txt',
        f'{video_id}/summary.txt',
    ]
    for filepath in files_required:
        if not gcs_file_exists(filepath):
            return False
    return True


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
    youtube_url, summary_ratio = params['youtube_url'], params['summary_ratio']
    video_id = extract_video_id_from_url(youtube_url)
    # Handle bad user input 
    if not youtube_url or not video_id:
        res = { 'error': 'You must provide a valid youtube_url as query string parameter' }
        return prepare_response(res, CODE_USER_ERROR)
    
    # Verify if video has been processed before and if the data is available
    if check_video_has_been_processed(video_id):
        
        res = {
            'metadata': '',
            'transcript': '',            
            'summary': '',
        }

    # Call f_youtube
    res_obj, res_code = f_youtube(youtube_url)
    if res_code == CODE_USER_ERROR or res_code == CODE_INTERNAL_ERROR:
        return prepare_response(res_obj, res_code)
    return prepare_response(res_obj, res_code)
