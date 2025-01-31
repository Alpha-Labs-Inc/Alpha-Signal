import './App.css'
import { ThemeProvider } from './components/theme-provider'
import Header from './components/header'

function App() {
  return (
    <>
      <ThemeProvider>
        <Header />
      </ThemeProvider>
    </>
  )
}

export default App
