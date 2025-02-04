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
  const fetchOrderData = async (type: number): Promise<Orders[]> => {
    const { data } = await axios.get(`http://127.0.0.1:8000/orders/${type}`)
    return data.orders
  }

  const { data } = useQuery<Orders[]>({
    queryKey: ['completed-order-history-data'],
    queryFn: () => fetchOrderData(2),
  })

  const { data: cancelledData } = useQuery<Orders[]>({
    queryKey: ['cancelled-order-history-data'],
    queryFn: () => fetchOrderData(3),
  })

  const headerRow = (
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
  )
  const emptyState = (
    <TableRow>
      <TableCell colSpan={7}>No orders history at this time.</TableCell>{' '}
    </TableRow>
  )

  const completedOrders = (
    <Card>
      <CardHeader>
        <CardTitle>Orders Completed</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          {headerRow}
          <TableBody>
            {data?.length === 0 && emptyState}
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

  const cancelledOrders = (
    <Card>
      <CardHeader>
        <CardTitle>Orders Cancelled</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          {headerRow}
          <TableBody>
            {cancelledData?.length === 0 && emptyState}
            {cancelledData?.map((order) => (
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

  return (
    <div>
      <div className="my-6">{completedOrders}</div>
      <div>{cancelledOrders}</div>
    </div>
  )
}

export default OrderHistory
