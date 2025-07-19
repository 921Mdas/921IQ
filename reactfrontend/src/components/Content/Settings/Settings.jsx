import React from 'react'
import Construction from '../../UnderConstruct/Construction'

const Settings = () => {
    const info = {
        message:'This feature is currently under development. Stay tuned for more control!',
        feature:'Settings'
    }
    
    return  <Construction data={info} />
}

export default Settings