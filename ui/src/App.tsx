import './App.css'
import { ThemeProvider } from './components/theme-provider'
import Header from './components/header'
import TableView from './components/wallet-table'
import OrderBalance from './components/order-balance'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { Toaster } from './components/ui/toaster'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import OrderHistory from './components/order-history'
import AutoBuy from './components/auto-buy'
import AutoSell from './components/auto-sell'
import ProfilesPage from './components/profiles'

function App() {
  const queryClient = new QueryClient()

  const homeNode = (
    <div className="container">
      <div className=" mx-auto p-4 m-4">
        <TableView />
      </div>
      <div className=" mx-auto p-4 m-4">
        <OrderBalance />
      </div>
    </div>
  )

  const configsNode = (
    <div className="grid grid-cols-3">
      <div className="max-w-xs">
        <AutoBuy />
      </div>
      <div className="max-w-xs">
        <AutoSell />
      </div>
    </div>
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Toaster />
        <Router>
          <Header />
          <div className="container mx-auto p-4 m-4">
            <Routes>
              <Route path="/" element={homeNode} />

              <Route path="/configure" element={configsNode} />

              <Route path="/order-history" element={<OrderHistory />} />

              <Route path="/signals" element={<ProfilesPage />} />
              {/* Add more routes here */}
            </Routes>
          </div>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
