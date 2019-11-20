import React from 'react'
import { useRouter } from 'next/router'

const Summary = () => {
  const router = useRouter()
  const { target } = router.query

  console.log('Summary got: ', target)
  return (
    <div>
      <p>This is the Summary page for {target}</p>
    </div>
  )
 }
export default Summary
