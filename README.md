# ViS - Video Summary

ViS (read as *Vice*) is an API that produces a text summary of a video based on a youtube link.

## ViS API

Simplified overview of the API:

1. A client calls the API with a youtube_url.
2. The API downloads the video metada, the video itself, and transforms the video into FLAC audio (function **f_youtube**).
3. The API transforms the audio file into a text transcript (function **f_transcript**).
4. The API generates a summary of the transcript (function **f_summary**).


The ViS API works as follows:

1) A client (a user or a web application) calls the ViS API.
   * This request must contain a youtube_url.
   * The API must validate the youtube_url.
     * if the URL is invalid, the API responds with a status code 400 and an error message.
2) The ViS API processes the youtube video:
   1. first, verify if the video exists in the GCS
      * if it does, great, return a 200 status code.
   2. otherwise, the ViS API calls the function *f_youtube*. This function:
      1. takes a youtube_url as input parameter.
      2. donwloads and stores **metadata** (title, author, duration, cover image, etc.) regarding the video. (400 status code if this fails, as it is likely a problem with the video url provided)
      3. downloads and stores the **video**. (500 status code if this fails)
      4. transforms the video into a **FLAC** audio file. (500 status code if this fails)
3) The ViS API generates the **full transcript**:
   1. first, verify if the full transcript already exists in the GCS
      * if it does, great, return 200 status code
   2. otherwise, the ViS API calls the function *f_transcript*. This function:
      1. takes a GCS URI that points to a FLAC audio file. (404 status code if the file can not be found)
      2. generates a full transcript and stores it into the GCS. (500 status code if this fails)
4) The ViS API generates the **summary**:
   1. first, verify if the summary already exists in the GCS
      * if it does, great, return 200 status code.
   2. otherwise, the ViS API calls the function *f_summary*. This function:
      1. takes a GCS URI that points to a text file, and a summary ratio value (between 0 and 1). (400 if this fails)
      2. generates the summary and store it into the GCS (500 if this fails)

### Functions

#### *f_api*

The **f_api** function implements the main API. It:
  * takes a youtube_url (required) and a summary_ratio (optional)
  * acts as a glue for the service, and calls the appropriate functions at each step.
  * returns:
    * status code 200 if success; otherwise, the success code of the failed function.
    * { transcript, summary, metadata }

#### *f_youtube*

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

#### *f_transcript*

The **f_transcript** function:
  * takes a GCS URI that points to a FLAC file (required)
  * verifies if the transcript already exists
    * returns 200 if so
  * calls the google Speech to Text API to generate a full transcript
    * returns 500 if this fails
  * returns object that points to the stored file: { transcript_URI }

#### **f_summary**

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


## Glossary

* GCS - Google Cloud Storage