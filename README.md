# ViS - Video Summary

ViS (read as *Vice*) is an API that produces a text summary of a video based on a youtube link.

- [ViS - Video Summary](#vis---video-summary)
  - [Issues](#issues)
  - [ViS API](#vis-api)
    - [Function f_api](#function-fapi)
    - [Function f_youtube](#function-fyoutube)
    - [Function f_transcript](#function-ftranscript)
    - [Function f_summary](#function-fsummary)
  - [ViS Frontend](#vis-frontend)
  - [Glossary](#glossary)
  - [Possibly useful links](#possibly-useful-links)
  - [Notes](#notes)
  - [Video processing](#video-processing)
  - [Possible refactors](#possible-refactors)


<hr />

## Issues

* Currently (20/12/2019) there are issues with pytube:
```
from pytube import YouTube
yt = YouTube('https://www.youtube.com/watch?v=DC471a9qrU4')
Traceback (most recent call last):
  File "<input>", line 1, in <module>
  File "/home/rafael/PycharmProjects/BlackHatPython/venv/lib/python3.6/site-packages/pytube/__main__.py", line 88, in __init__
    self.prefetch_init()
  File "/home/rafael/PycharmProjects/BlackHatPython/venv/lib/python3.6/site-packages/pytube/__main__.py", line 97, in prefetch_init
    self.init()
  File "/home/rafael/PycharmProjects/BlackHatPython/venv/lib/python3.6/site-packages/pytube/__main__.py", line 143, in init
    mixins.apply_descrambler(self.player_config_args, fmt)
  File "/home/rafael/PycharmProjects/BlackHatPython/venv/lib/python3.6/site-packages/pytube/mixins.py", line 96, in apply_descrambler
    for i in stream_data[key].split(',')
KeyError: 'url_encoded_fmt_stream_map'
```

Pytube has multiple open issues regarding this error, f.e., https://github.com/nficano/pytube/issues/531 and https://github.com/nficano/pytube/issues/529.



<hr />


## ViS API

Simplified overview of the API:

1. A client calls the API with a youtube_url.
2. The API downloads the video metada, the video itself, and transforms the video into FLAC audio (function **f_youtube**).
3. The API transforms the audio file into a text transcript (function **f_transcript**).
4. The API generates a summary of the transcript (function **f_summary**).

Note: these *functions* are not actually google cloud functions, although they could be. The reason to not make them separate functions is two-fold: 1) less overhead in terms of deploying multiple functions; 2) uncertainty around how to re-use code across multiple functions, particularly regarding the google cloud storage logic. Thus, these functions will be logically isolated in their own files, but the API will be a single google cloud function. 

### Function *f_api*

The **f_api** function implements the main API. It:
  * takes a youtube_url (required) and a summary_ratio (optional)
  * acts as a glue for the service, and calls the appropriate functions at each step.
  * returns:
    * status code 200 if success; otherwise, the success code of the failed function.
    * { transcript, summary, metadata }

### Function *f_youtube*

The **f_youtube** function:
  * takes a youtube_url (required)
  * verifies if this video has been (sucessfully) processed before. 
    * returns 200 if so. 
  * downloads and stored video metadata
    * at least *title*, *description*, *duration*, *author*, possibly cover image.
    * returns 400 if this fails (as youtube_url is probably wrong - bad user input)
  * downloads and stores the video
    * returns 403 if forbidden, or 500 if download fails for other reason
  * transforms video into FLAC
    * returns 500 if this fails.
  * returns object that points to the stored files: { metada_URI, video_URI, flac_URI }

### Function *f_transcript*

The **f_transcript** function:
  * takes a GCS URI that points to a FLAC file (required)
  * verifies if the transcript already exists
    * returns 200 if so
  * calls the google Speech to Text API to generate a full transcript
    * returns 500 if this fails
  * returns object that points to the stored file: { transcript_URI }

### Function **f_summary**

The **f_summary** function:
  * takes a GCS URI that points to a *transcript* text file (required) and a summary_ratio (optional)
  * verifies if the summary already exists
    * returns 200 if so
  * calls the google Gensim API to generate a short summary transcript
    * returns 500 if this fails
  * returns object that points to the stored file: { summary_URI }


<hr />


## ViS Frontend

The ViS Frontend is implemented by a Website that allows a user to select a youtube_url that will be used to generate a full transcript and a short summary.

Features:
  * generates a full transcript based on youtube_url
  * generates a short summary based on youtube_url
  * handle errors gracefully
  * display loading info, status update and estimated processing time.
  * display video information


<hr />


## Glossary

* GCS - Google Cloud Storage

## Possibly useful links

https://transcribefiles.net/other/pages/caption-subtitle-converter.htm

https://www.youtube.com/api/timedtext?v=9_-wndK57Ls&asr_langs=de,en,es,fr,it,ja,ko,nl,pt,ru&caps=asr&hl=pt-PT&ip=0.0.0.0&ipbits=0&expire=1574324893&sparams=ip,ipbits,expire,v,asr_langs,caps&signature=E75B11519446396B4CE5357D6A56418E60D6CA67.1A1CB2D63B3A220871F91D156BE6E208D039622F&key=yt8&kind=asr&lang=en


## Notes

* it might NOT be necessary to use google Speech 2 Text
  * Youtube provides captions (there are always auto generated captions at least), which can be even better than the ones generated by google s2t
  * this might require the processing of the captions to a text format.
  * this would probably also eliminate the need to download the video...

* we should verify if the video has been processed, BEFORE creating a YouTube instance. 
  * This is because (I believe) pytube makes requests to youtube as soon as you instantiate the class
  * thus, instantiates the class in the beggining contributes to youtube spam
  * which contributes to youtube blocking us much often

## Video processing 

Upon processing a youtube video (with `video_id`), the following files are created in GCS, under the `video_id` folder:
  * video.mp4
  * audio.flac
  * metadata.json
  * transcript.txt
  * summmary.txt


## Possible refactors

* We are reading from local and to local storage
  * This can be quite slow.
  * Ideally we want to keep it all inside the python runtime if possible
  * instead of `blob.download_to_filename(fpath)` we would like to download to a variable
