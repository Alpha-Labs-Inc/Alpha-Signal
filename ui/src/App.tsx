import './App.css'
import { ThemeProvider } from './components/theme-provider'
import { Button } from './components/ui/button'

const Header = () => {
  return (
    <div className="w-full flex justify-between items-center w-100">
      <span className="text-lg font-medium">AlphaSigma</span>
      <Button>Wallet</Button>
    </div>
  )
}

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
