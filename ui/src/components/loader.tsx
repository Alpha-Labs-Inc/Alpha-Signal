import { useEffect, useState } from 'react'

const Loader = () => {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setLoading((prev) => !prev) // Toggles state if needed
    }, 2000) // Adjust timing if needed

    return () => clearInterval(interval)
  }, [])

  return (
    <div className='flex w-full justify-center'><div className="w-12 h-12 border-4 border-transparent border-t-white rounded-full animate-spin" /></div>
  )
}

export default Loader
