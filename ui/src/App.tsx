import './App.css'
import { ThemeProvider } from './components/theme-provider'
import Header from './components/header'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './components/ui/table'

const TableView = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Wallet</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableCaption>A list of your holdings</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Token Name</TableHead>
              <TableHead>Mint Address</TableHead>
              <TableHead>Balance</TableHead>
              <TableHead className="text-right">Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium text-left">Sol</TableCell>
              <TableCell className="text-left">
                asdfasdfasdfasdf;lkjasdf;
              </TableCell>
              <TableCell className="text-left">1.44</TableCell>
              <TableCell className="text-right">$250.00</TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium text-left">Sol</TableCell>
              <TableCell className="text-left">
                asdfasdfasdfasdf;lkjasdf;
              </TableCell>
              <TableCell className="text-left">1.44</TableCell>
              <TableCell className="text-right">$250.00</TableCell>
            </TableRow>

            <TableRow>
              <TableCell className="font-medium text-left">Sol</TableCell>
              <TableCell className="text-left">
                asdfasdfasdfasdf;lkjasdf;
              </TableCell>
              <TableCell className="text-left">1.44</TableCell>
              <TableCell className="text-right">$250.00</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

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
