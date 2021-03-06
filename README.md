# ViS - Video Summary

ViS (read as *Vice*) is an API that produces a text summary of a video based on a youtube link.

- [ViS - Video Summary](#vis---video-summary)
  - [ViS API](#vis-api)
    - [Function *f_api*](#function-fapi)
    - [Function *f_youtube*](#function-fyoutube)
    - [Function *f_transcript*](#function-ftranscript)
    - [Function **f_summary**](#function-fsummary)
  - [ViS Frontend](#vis-frontend)
  - [Glossary](#glossary)


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
    * at least *title*, *duration*, *author*, possibly cover image.
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

The ViS Frontend is a Website that allows a user to select a youtube_url that will be used to generate a full transcript and a short summary.

Features:
  * generates a full transcript based on youtube_url
  * generates a short summary based on youtube_url
  * handle errors gracefully
  * display loading info, status update and estimated processing time.


<hr />


## Glossary

* GCS - Google Cloud Storage

