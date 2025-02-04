import { useQuery } from '@tanstack/react-query'
import { Orders } from './order-balance'
import axios from 'axios'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table'

const OrderHistory = () => {
  const fetchOrderData = async (): Promise<Orders[]> => {
    const { data } = await axios.get('http://127.0.0.1:8000/orders/2')
    return data.orders
  }

  const { data } = useQuery<Orders[]>({
    queryKey: ['order-history-data'],
    queryFn: fetchOrderData,
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Orders Completed</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Mint Address</TableHead>
              <TableHead>Last Price Max</TableHead>
              <TableHead>Sell Mode</TableHead>
              <TableHead>Sell Value</TableHead>
              <TableHead>Time Added</TableHead>
              <TableHead className="text-right">Balance</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.length === 0 && (
              <TableRow>
                <TableCell colSpan={7}>No orders at this time</TableCell>{' '}
                {/* Updated colSpan */}
              </TableRow>
            )}
            {data?.map((order) => (
              <TableRow key={order.id}>
                <TableCell className="text-left">
                  {order.mint_address}
                </TableCell>
                <TableCell>{order.last_price_max}</TableCell>
                <TableCell>{order.sell_mode}</TableCell>
                <TableCell>{order.sell_value}</TableCell>
                <TableCell>{order.time_added}</TableCell>
                <TableCell className="text-right">{order.balance}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default OrderHistory
