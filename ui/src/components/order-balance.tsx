import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table'
import axios from 'axios'
import { useQuery } from '@tanstack/react-query'
import Loader from './loader'
import { Button } from './ui/button'

export interface Orders {
  id: string
  mint_address: string
  last_price_max: number
  sell_mode: string
  sell_value: number
  sell_type: string
  time_added: string
  balance: number
}

const fetchOrderData = async (): Promise<Orders[]> => {
  const { data } = await axios.get('http://127.0.0.1:8000/orders/0')
  return data.orders
}

const cancelOrder = async (orderId: string) => {
  await axios.delete(`http://127.0.0.1:8000/orders/cancel/${orderId}`)
}

const OrderBalance = () => {
  const { data, error, isLoading, refetch } = useQuery<Orders[]>({
    queryKey: ['order-data'],
    queryFn: fetchOrderData,
  })

  if (isLoading) return <Loader />
  if (error) return <div>Error loading data</div>

  const handleCancel = (orderId: string) => {
    cancelOrder(orderId).then(() => refetch())
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Order Balance</CardTitle>
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
              <TableHead>Actions</TableHead> {/* Add header for actions */}
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
                <TableCell>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleCancel(order.id)}
                  >
                    Cancel
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default OrderBalance
