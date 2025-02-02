import './App.css'
import { ThemeProvider } from './components/theme-provider'
import Header from './components/header'
import TableView from './components/wallet-table'
import OrderBalance from './components/order-balance'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'

function App() {
  const queryClient = new QueryClient()

  return (
    <>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <div className="container">
            <Header />

            <div className=" mx-auto p-4 m-4">
              <TableView />
            </div>
            <div className=" mx-auto p-4 m-4">
              <OrderBalance />
            </div>
          </div>
        </ThemeProvider>
      </QueryClientProvider>
    </>
  )
}

export default App
