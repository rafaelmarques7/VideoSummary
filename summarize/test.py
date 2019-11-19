from gensim.summarization.summarizer import summarize

# Function to summarize text
def get_summary():
    # text=b"I'm sorry I didn't get your name I got yours.\n I just want you to know.\n I just want you to know how sorry we are that that things got so fucked up with us.\n oh I'm sorry did I break your concentration.\n I didn't mean to do that you were saying something about best intentions.\n what's the matter.\n allow me to retort.\n what does Marcellus Wallace look like.\n give me the Bible verse Ezekiel 25:17.\n the path of the righteous man is beset on all sides.\n who in the name of Charity and good-will of lost 2 and I will strike..\n"
    text=b"I'm sorry I didn't get your name I got yours. I just want you to know. I just want you to know how sorry we are that that things got so fucked up with us.\n oh I'm sorry did I break your concentration.\n I didn't mean to do that you were saying something about best intentions.\n what's the matter.\n allow me to retort.\n what does Marcellus Wallace look like.\n give me the Bible verse Ezekiel 25:17.\n the path of the righteous man is beset on all sides.\n who in the name of Charity and good-will of lost 2 and I will strike..\n"
    # Get full text
    # blob = bucket.get_blob(input_filename)
    # text = blob.download_as_string()
    # Call the summarize API
    body = summarize(str(text), 0.5)
    print(f'body: {body}, type(body): {type(body)}')
    # Write to GCS     
    # blob = bucket.blob(output_filename)
    # blob.upload_from_string(body, content_type="text/plain")
    # return body

get_summary()