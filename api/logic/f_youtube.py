import traceback
from pytube import YouTube
from pydub import AudioSegment
from .gcs import gcs_file_exists, gcs_upload_file
from .helper import write_text_to_file, write_json_to_file
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


# Function to extract youtube generated captions. Returns a local filepath
def get_youtube_captions(yt_instance):
    captions = yt_instance.captions.all()[0].generate_srt_captions()
    fpath_local = '/tmp/captions.srt'
		write_to_file(captions, fpath_local)
    return fpath_local


# Function to transform srt to txt. Returns captions_text, fpath_local.
def clean_youtube_captions(fpath_local, linebreak='\n'):
    captions_text = ''
    captions_srt = pysrt.open(fpath_local)
    for sub in captions_srt:
        captions_text = captions_text + sub.text + linebreak
    fpath_local = '/tmp/captions.txt'
		write_to_file(captions_text, fpath_local)
    return captions_text, fpath_local


# Youtube processing function
def f_youtube(youtube_url):
	""" This function processes a youtube video.
	
		This function does:
		1) verify if video was processed before, and skips if so. (verify all parts exist)
		2) download and store video metadata
		3) download and store youtube captions
		(optional)
		4) download and store video
		5) convert video to audio (.flac)
	""" 
	
	# Instantiate youtube object. This throws error if youtube_url is invalid.
	try:
		yt_instance = YouTube(youtube_url)
	except Exception as e:
		res = {
			'error': 'Could not create YouTube instance. This is probably due to an invalid youtube_url',
			'traceback': str(traceback.format_exc()),
		}	
		return res, CODE_USER_ERROR
	
	# Get metadata and youtube_id
	yt_metadata = youtube_get_metadata(yt_instance)
	yt_id = yt_metadata['video_id']
	
	# The full path to the necessary files in the bucket 
	bucket_path_video = f'{yt_id}/video.mp4'
	bucket_path_audio = f'{yt_id}/audio.flac'	
	bucket_path_metadata = f'{yt_id}/metadata.json'
	bucket_path_captions = f'{yt_id}/captions.txt'

	# Verify if metadata exists in GCS. Upload it if it does not.
	if not gcs_file_exists(bucket_path_metadata):
		local_fpath = '/tmp/metadata.json'
		write_json_to_file(yt_metadata, local_fpath)
		gcs_upload_file(local_fpath, bucket_path_metadata)

	# Get, process and upload youtube captions
	fpath_captions_srt = get_youtube_captions(yt_instance)
	captions_txt, fpath_captions_txt = clean_youtube_captions(fpath_captions_srt)
	gcs_upload_file(fpath_captions_txt, bucket_path_captions)

	# Build and return a response
	res_obj = {
		'url': youtube_url,
		'metadata': yt_metadata,
		'captions': captions_txt,
	}
	return res_obj, CODE_SUCCESS
