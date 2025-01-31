import './App.css'
import { ThemeProvider } from './components/theme-provider'
import Header from './components/header'
import TableView from './components/wallet-table'
function App() {
  return (
    <>
      <ThemeProvider>
        <div className="container">
          <Header />

          <div className=" mx-auto p-4 m-4">
            <TableView />
          </div>
        </div>
      </ThemeProvider>
    </>
  )
}

export default App
