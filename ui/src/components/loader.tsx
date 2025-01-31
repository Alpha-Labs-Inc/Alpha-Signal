import { useState, useEffect } from 'react'
import { Progress } from './ui/progress'

const Loader = () => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 10))
    }, 300)
    return () => clearInterval(interval)
  }, [])

  return <Progress value={progress} />
}

export default Loader
