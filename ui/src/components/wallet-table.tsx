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
import axios from 'axios'
import { useQuery } from '@tanstack/react-query'
import Loader from './loader'

interface WalletToken {
  token_name?: string;
  token_ticker?: string;
  image?: string;
  mint_address: string;
  balance: number;
  value: number;
  usd_balance?: number;  // <-- Added this
}

const fetchWalletData = async (): Promise<{
  wallet_tokens: WalletToken[]
  total_value: number
}> => {
  const { data } = await axios.get('http://localhost:8000/wallet-value')
  return data
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text).catch(err => console.error('Failed to copy:', err));
}

const formatNumber = (num: number | undefined): string => {
  if (num === undefined) return "0.00";
  return num % 1 === 0 ? `${num.toFixed(2)}` : `${num}`;
};

const TableView = () => {
  const { data, error, isLoading } = useQuery({
    queryKey: ['wallet-data'],
    queryFn: fetchWalletData,
  })

  if (isLoading) return <Loader />
  if (error) return <div>Error loading data</div>

  const walletTokens = data?.wallet_tokens || []
  const totalValue = data?.total_value || 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wallet</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead></TableHead>
              <TableHead>Ticker</TableHead>
              <TableHead>Mint Address</TableHead>
              <TableHead>Balance</TableHead>
              <TableHead className="text-right">Value</TableHead>
              <TableHead className="text-right">USD Balance</TableHead> {/* <-- Added Column */}
            </TableRow>
          </TableHeader>
          <TableBody>
            {walletTokens.length > 0 ? (
              walletTokens.map((token, index) => (
                <TableRow key={index}>
                  <TableCell className="text-left">
                    {token.image && (
                      <img
                        src={token.image}
                        alt={token.token_name || 'Token'}
                        className="w-12 h-12 rounded-lg border-2 border-white"
                      />
                    )}
                  </TableCell>
                  <TableCell className="font-medium text-left">
                    <span className="relative group cursor-pointer">
                      {token.token_ticker}
                      {token.token_name && (
                        <span className="absolute left-1/2 transform -translate-x-1/2 bottom-full mb-2 w-auto px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity">
                          {token.token_name}
                        </span>
                      )}
                    </span>
                  </TableCell>
                  <TableCell className="text-left cursor-pointer relative group" onClick={() => copyToClipboard(token.mint_address)}>
                    {token.mint_address}
                    <span className="absolute left-1/2 transform -translate-x-1/2 bottom-full mb-2 w-auto px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity">
                      Click to copy
                    </span>
                  </TableCell>
                  <TableCell className="text-left">{formatNumber(token.balance)}</TableCell>
                  <TableCell className="text-right">
                    ${formatNumber(token.value)}
                  </TableCell>
                  <TableCell className="text-right">
                    ${token.usd_balance?.toFixed(2) || "0.00"} {/* <-- Added USD Balance */}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="text-center">
                  No tokens found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <div className="text-right font-bold mt-4">
          Total Wallet Value: ${totalValue.toFixed(2)}
        </div>
      </CardContent>
    </Card>
  )
}

export default TableView
