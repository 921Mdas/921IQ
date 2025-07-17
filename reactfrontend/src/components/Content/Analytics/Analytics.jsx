import React from 'react'
import Construction from '../../UnderConstruct/Construction'

const Analytics = () => {
  const info = {
    message:'This feature is currently under development. Stay tuned for powerful insights!',
    feature:'Analytics'
  }
  return (
    <Construction data={info} />
  )
}

export default Analytics