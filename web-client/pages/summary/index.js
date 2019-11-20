import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

const API_ENDPOINT = 'http://europe-west1-videosummary.cloudfunctions.net/video_summary_function';

const Summary = () => {
  // routing
  const router = useRouter()
  const { youtube_url } = router.query
  // state management
  const [hasError, setError] = useState(false)
  const [data, setData] = useState({})

  async function fetchData() {
    console.log('inside fetchData')
    // call the API once only!
    if (!hasError && Object.entries(data).length === 0) {
      const request_url = `${API_ENDPOINT}?youtube_url=${youtube_url}`;
      console.log('making API request to: ', request_url)
      const res = await fetch(request_url)
      res
        .json()
        .then(res => setData(res))
        .catch(err => setError(err))
    }
  }

  useEffect(() => {
    fetchData()
  })

  console.log('Summary got: ', youtube_url, data, hasError)
  return (
    <div>
      <p>This is the Summary page for {youtube_url}</p>
      <hr />
      <p>Summary:</p>
      <p>{data ? data.summary : null}</p>
      <hr />
      <p>Full text:</p>
      <p>{data ? data.text : null}</p>
    </div>
  )
 }
export default Summary



