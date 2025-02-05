import { useState } from 'react'
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
import { useToast } from '@/hooks/use-toast'
import { useQuery } from '@tanstack/react-query'
import { RefreshCcw, Loader2 } from 'lucide-react'
import Loader from './loader'
import { Button } from './ui/button'
import { FiCheck } from 'react-icons/fi'

interface WalletToken {
  token_name?: string
  token_ticker?: string
  image?: string
  mint_address: string
  balance: number
  value: number
  usd_balance?: number
  change_24hr?: number
  change_6hr?: number
  change_1hr?: number
  change_5min?: number
  percent_change_24hr?: number
  percent_change_6hr?: number
  percent_change_1hr?: number
  percent_change_5min?: number
}

const fetchWalletData = async (): Promise<{
  wallet_tokens: WalletToken[]
  total_value: number
  percent_change_value_24h: number

}> => {
  try {
    const { data } = await axios.get('http://localhost:8000/wallet-value')
    return data
  } catch (error) {
    console.error('Error fetching wallet data:', error)
    return { wallet_tokens: [], total_value: 0, percent_change_value_24h: 0 }
  }
}

const TableView = () => {
  const { data, error, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['wallet-data'],
    queryFn: fetchWalletData,
  })

  const { toast } = useToast()
  const [copiedToken, setCopiedToken] = useState<string | null>(null)

  const copyToClipboard = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setCopiedToken(text)
        toast({
          title: 'Address Copied',
          description: `The address ${text} has been copied to your clipboard.`,
          duration: 2000,
        })
        setTimeout(() => setCopiedToken(null), 2000)
      })
      .catch((err) => console.error('Failed to copy:', err))
  }

  const formatNumber = (num: number): string => {
    return num % 1 === 0 ? `${num.toFixed(2)}` : `${num}`
  }


  const formatPriceChange = (price?: number, percent?: number) => {
    if (price === undefined || price === null || percent === undefined || percent === null) return '-';
    const formatted = `$${price.toFixed(2)} (${percent.toFixed(2)}%)`;
    return (
      <span className={percent > 0 ? 'text-green-500' : percent < 0 ? 'text-red-500' : ''}>
        {formatted}
      </span>
    );
  };

  const formatMintAddress = (address: string): string => {
    return `${address.slice(0, 6)}...${address.slice(-6)}`
  }

  if (isLoading) return <Loader />
  if (error) return <div>Error loading data</div>
  if (!data || !data.wallet_tokens) return <div>No wallet data available</div>

  const walletTokens = data.wallet_tokens
  const totalValue = data.total_value
  const percentChangeValue24h = data?.percent_change_value_24h || 0

  return (
    <Card className={`shadow-md ${percentChangeValue24h !== 0 ? '' : ''}`}
      style={{
        backgroundColor: percentChangeValue24h > 0
          ? 'rgba(0, 255, 0, 0.01)'  // Very subtle green tint
          : percentChangeValue24h < 0
            ? 'rgba(255, 0, 0, 0.01)'  // Very subtle red tint
            : 'transparent'
      }}>
      <CardHeader className="relative flex items-center justify-center">
        <CardTitle className="absolute left-1/2 transform -translate-x-1/2 text-lg">
          Wallet
        </CardTitle>
        <Button
          onClick={() => refetch()}
          className="ml-auto flex items-center justify-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 active:scale-95 transition-transform"
          disabled={isFetching}
        >
          {isFetching ? <Loader2 size={18} className="animate-spin" /> : <RefreshCcw size={18} />}
        </Button>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead></TableHead>
              <TableHead>Ticker</TableHead>
              <TableHead>Mint Address</TableHead>

              <TableHead className="text-center">Value</TableHead>
              <TableHead className="text-center">24 Hour Change</TableHead>
              {/* <TableHead className="text-center">6h Change</TableHead>
              <TableHead className="text-center">1h Change</TableHead>
              <TableHead className="text-center">5m Change</TableHead> */}
              <TableHead className="text-center">Balance</TableHead>
              <TableHead className="text-right">USD Balance</TableHead>
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
                        className="w-12 h-12 rounded-lg"
                      />
                    )}
                  </TableCell>
                  <TableCell className="font-medium text-left relative group cursor-pointer">
                    <span>{token.token_ticker}</span>
                    {token.token_name && (
                      <div className="absolute left-1/2 transform -translate-x-1/2 translate-y-[-200%] px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {token.token_name}
                      </div>
                    )}
                  </TableCell>
                  <TableCell
                    className="text-left cursor-pointer relative group"
                    onClick={() => copyToClipboard(token.mint_address)}
                  >
                    <span>{formatMintAddress(token.mint_address)}</span>
                    <div className="absolute left-1/2 transform -translate-x-1/2 translate-y-[-250%] px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                      {token.mint_address}
                    </div>
                    <Button
                      variant={'ghost'}
                      className="bg-inherit ml-2 p-1 rounded relative z-20"
                    >
                      {copiedToken === token.mint_address ? (
                        <FiCheck className="w-4 h-4 text-white" />
                      ) : (
                        <img
                          src="/copy.svg"
                          alt="Copy"
                          className="w-4 h-4 filter invert brightness-0"
                        />
                      )}
                    </Button>
                  </TableCell>

                  <TableCell className="text-center">
                    ${formatNumber(token.value)}
                  </TableCell>
                  <TableCell className="text-center">{formatPriceChange(token.change_24hr, token.percent_change_24hr)}</TableCell>
                  {/* <TableCell className="text-right">{formatPriceChange(token.change_6hr, token.percent_change_6hr)}</TableCell>
                  <TableCell className="text-right">{formatPriceChange(token.change_1hr, token.percent_change_1hr)}</TableCell>
                  <TableCell className="text-right">{formatPriceChange(token.change_5min, token.percent_change_5min)}</TableCell> */}
                  <TableCell className="text-center">
                    {formatNumber(token.balance)}
                  </TableCell>
                  <TableCell className="text-right">
                    ${token.usd_balance?.toFixed(2) || '0.00'}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="text-center">
                  No tokens found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <div className="text-right font-bold mt-4">
          Total Wallet Value: $ {totalValue.toFixed(2)}  <span className={percentChangeValue24h > 0 ? 'text-green-500' : percentChangeValue24h < 0 ? 'text-red-500' : 'text-white'}>
            ({percentChangeValue24h.toFixed(2)}%)
          </span>
        </div>
      </CardContent>
    </Card >
  )
}

export default TableView
