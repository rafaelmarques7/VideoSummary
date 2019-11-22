from google.cloud import storage as gcs

def read_file(gcs_full_filepath):
  """ params: gcs_full_filepath - bucket_name/(subfolders)/filename """
  gcs_file = gcs.open(gcs_full_filepath)
  contents = gcs_file.read()
  gcs_file.close()
  print('downloaded content: \n', contents)

fpath = 'video_summary_bucket/1w2t3EWmlVU/summary.txt'
read_file(fpath)