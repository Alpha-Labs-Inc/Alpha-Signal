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
}

const fetchWalletData = async (): Promise<{
  wallet_tokens: WalletToken[]
  total_value: number
}> => {
  const { data } = await axios.get('http://localhost:8000/wallet-value')
  return data
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

  const formatMintAddress = (address: string): string => {
    return `${address.slice(0, 6)}...${address.slice(-6)}`
  }

  if (isLoading) return <Loader />
  if (error) return <div>Error loading data</div>

  const walletTokens = data?.wallet_tokens || []
  const totalValue = data?.total_value || 0

  return (
    <Card className="{walletTokens.length > 0 ? 'rounded-lg' : 'bg-transparent'} shadow-md">
      <CardHeader className="relative flex items-center justify-center">
        <CardTitle className="absolute left-1/2 transform -translate-x-1/2 text-lg">
          Wallet
        </CardTitle>
        <Button
          onClick={() => refetch()}
          className="ml-auto flex items-center justify-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 active:scale-95 transition-transform"
          disabled={isFetching}
        >
          {isFetching ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <RefreshCcw size={18} />
          )}
        </Button>
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
                    <div className="absolute left-1/2 transform -translate-x-1/2 translate-y-[-200%] px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
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
                  <TableCell className="text-left">
                    {formatNumber(token.balance)}
                  </TableCell>
                  <TableCell className="text-right">
                    ${formatNumber(token.value)}
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
          Total Wallet Value: ${totalValue.toFixed(2)}
        </div>
      </CardContent>
    </Card>
  )
}

export default TableView
