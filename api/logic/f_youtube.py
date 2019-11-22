import traceback
from pytube import YouTube
from pydub import AudioSegment
from .gcs import gcs_file_exists, gcs_upload_file
from constants import BUCKET_NAME, CODE_SUCCESS, \
    CODE_USER_ERROR, CODE_INTERNAL_ERROR, SUMMARY_RATIO_DEFAULT


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


# Function to extract video metadata. 
# Contains title, video_id, desctiption, (author, duration, image).
def youtube_get_metadata(yt_instance):
	metadata = {}
	try:
		metadata = {
			'title': yt_instance.title,
			'video_id': yt_instance.video_id,
			'description': yt_instance.description,
			'author': yt_instance.player_config_args['player_response']['videoDetails']['author'],
			'duration': yt_instance.player_config_args['player_response']['videoDetails']['lengthSeconds'],
			'image_url': yt_instance.player_config_args['player_response']['videoDetails']['thumbnail']['thumbnails'][-1]['url'],
		}
	except Exception as e:
		print('Could not extract metadata. Error: ', str(traceback.format_exc()))
	return metadata


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


# Youtube processing function
def f_youtube(youtube_url):
	""" This function processes a youtube video.
	
		This function does:
		1) verify if video was processed before, and skips if so. (verify all parts exist)
		2) downloads and stores video metadata
		3) download and store video
		4) convert video to audio (.flac)
	""" 
	# Instantiate youtube object. This throws error if youtube_url is invalid.
	try:
		yt_instance = YouTube(youtube_url)
	except Exception as e:
		res = {
			'error': 'Could not create YouTube instance. This is probably due to bad youtube_url',
			'traceback': str(traceback.format_exc()),
		}	
		return res, CODE_USER_ERROR
	# Get metadata and youtube_id
	print(yt_instance.__dict__)
	yt_metadata = youtube_get_metadata(yt_instance)
	print(yt_metadata)
	return {}, 200
	yt_id = yt_metadata['video_id']
	# The full path to the necessary files in the bucket 
	bucket_path_video = f'{yt_id}/video.mp4'
	bucket_path_audio = f'{yt_id}/audio.flac'	
	bucket_path_metadata = f'{yt_id}/metadata.json'
	# Verify if metadata exists in GCS. Upload it if it does not.
	if not gcs_file_exists(bucket_path_metadata):
		# write to temporary file
		local_fpath = '/tmp/metadata.json'
		with open(local_fpath, 'w') as f:
			json.dump(yt_metadata, f)
		# upload file
		gcs_upload_file(local_fpath, bucket_path_metadata)
	return {'uri_metada': bucket_path_metadata}, CODE_SUCCESS
