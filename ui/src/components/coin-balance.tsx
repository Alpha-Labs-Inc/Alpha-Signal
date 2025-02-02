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

interface Orders {
  id: string
  mint_address: string
  last_price_max: number
  sell_mode: string
  sell_value: number
  sell_type: string
  time_added: string
  balance: number
}

const fetchCoinData = async (): Promise<Orders[]> => {
  const { data } = await axios.get('http://127.0.0.1:8000/order/tracked')
  return data.orders
}

const CoinBalance = () => {
  const { data, error, isLoading } = useQuery<Orders[]>({
    queryKey: ['coin-data'],
    queryFn: fetchCoinData,
  })

  if (isLoading) return <Loader />
  if (error) return <div>Error loading data</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle>Coin Balance</CardTitle>
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
                <TableCell colSpan={6}>No orders at this time</TableCell>
              </TableRow>
            )}
            {data?.map((coin) => (
              <TableRow key={coin.id}>
                <TableCell className="text-left">{coin.mint_address}</TableCell>
                <TableCell>{coin.last_price_max}</TableCell>
                <TableCell>{coin.sell_mode}</TableCell>
                <TableCell>{coin.sell_value}</TableCell>
                <TableCell>{coin.time_added}</TableCell>
                <TableCell className="text-right">{coin.balance}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default CoinBalance
