import React, { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import InputForm from '../components/inputForm'

const Home = () => {

  return (
    <div>
      <Head>
        <title>Home page</title>
      </Head>
      <div>
        <p>Header yeah</p>
        <p>Main Description</p>
      </div>
      <div>
        <p>here is the input form</p>
        <InputForm />
        <Link href="/summary/[myurl]" as="/summary/url">
          <a>click me</a>
        </Link>
      </div>
    </div>
  )
}

export default Home
