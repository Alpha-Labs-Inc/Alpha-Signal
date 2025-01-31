import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table'

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

export default TableView
