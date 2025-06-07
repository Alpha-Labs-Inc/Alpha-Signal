import { useState, useEffect } from 'react'
import { HoverCard, HoverCardContent, HoverCardTrigger } from './ui/hover-card'
import { Avatar, AvatarImage } from './ui/avatar'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useToast } from '@/hooks/use-toast'
import { Button } from './ui/button'

const Header = () => {
  const { toast } = useToast()
  const [walletData, setWalletData] = useState<{
    sol_balance: number
    usd_value: number
    percent_change_24hr: number
  } | null>(null)
  const [walletKey, setWalletKey] = useState<string | null>(null)
  const [fullWalletKey, setFullWalletKey] = useState<string | null>(null)
  const [, setLoading] = useState(true)
  const [, setCopied] = useState(false)
  const [showTooltip, setShowTooltip] = useState(false)

  useEffect(() => {
    const fetchWalletKey = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/load-wallet')
        if (data?.public_key) {
          setFullWalletKey(data.public_key)
          setWalletKey(
            `${data.public_key.slice(0, 3)}...${data.public_key.slice(-3)}`
          )
        } else {
          setWalletKey('N/A')
        }
      } catch (error) {
        console.error('Error fetching wallet key:', error)
        setWalletKey('Error')
      }
    }

    const fetchSolValue = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/sol-value')
        if (
          data?.balance !== undefined &&
          data?.usd_balance !== undefined &&
          data?.percent_change_24hr !== undefined
        ) {
          setWalletData({
            sol_balance: data.balance,
            usd_value: data.usd_balance,
            percent_change_24hr: data.percent_change_24hr,
          })
        } else {
          setWalletData({
            sol_balance: 0,
            usd_value: 0,
            percent_change_24hr: 0,
          })
        }
      } catch (error) {
        console.error('Error fetching SOL value:', error)
        setWalletData({ sol_balance: 0, usd_value: 0, percent_change_24hr: 0 })
      } finally {
        setLoading(false)
      }
    }

    fetchWalletKey()
    fetchSolValue()
  }, [])

  const copyToClipboard = () => {
    if (fullWalletKey) {
      navigator.clipboard.writeText(fullWalletKey)
      setCopied(true)
      toast({
        title: 'Address Copied',
        description: `The address ${fullWalletKey} has been copied to your clipboard.`,
        duration: 2000,
      })
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleSendSol = async () => {
    const to = window.prompt('Destination wallet address:')
    if (!to) return
    const amtStr = window.prompt('Amount of SOL to send:')
    if (!amtStr) return
    const amt = parseFloat(amtStr)
    if (isNaN(amt) || amt <= 0) {
      toast({ title: 'Error', description: 'Enter a valid amount' })
      return
    }
    try {
      const { data } = await axios.post('http://localhost:8000/send-sol', {
        destination: to,
        amt,
      })
      console.log(data)
      toast({ title: 'SOL Sent', description: '' })
    } catch (err) {
      console.error('Send SOL error:', err)
      toast({ title: 'Error', description: 'Failed to send SOL' })
    }
  }

  const navigate = useNavigate()
  return (
    <div className="w-full flex justify-between items-center px-4 py-3">
      <HoverCard>
        <HoverCardTrigger
          asChild
          className="flex items-center space-x-2 cursor-pointer"
        >
          <span
            onClick={() => navigate('/')}
            className="text-3xl hover:underline font-bold flex items-center"
          >
            Alpha Signal
            <Avatar className="ml-2">
              <AvatarImage src="../assets/logo.jpg" alt="logo" />
            </Avatar>
          </span>
        </HoverCardTrigger>
        <HoverCardContent className="w-80">
          <div className="flex flex-col space-y-2">
            <h4 className="text-sm font-semibold">Alpha Labs Inc</h4>
            <p className="text-sm">AI Algorithmic Trading for the Blockchain</p>
            <span className="text-xs text-muted-foreground">
              Find us at <a href="https://x.com/_AlphaSignal_">@_AlphaSignal_</a> on X
            </span>
          </div>
        </HoverCardContent>
      </HoverCard>

      <div className="ml-auto flex items-center space-x-4">
        <HoverCard>
          <HoverCardTrigger asChild>
            <div
              onClick={() => navigate('/')}
              className="mr-4 text-base hover:underline cursor-pointer"
            >
              Wallet
            </div>
          </HoverCardTrigger>
          <HoverCardContent className="shadow-md relative">
            <div
              className="absolute inset-0 rounded-md"
              style={{
                background:
                  (walletData?.percent_change_24hr ?? 0) > 0
                    ? 'rgba(0, 255, 0, 0.02)' // Subtle green overlay
                    : (walletData?.percent_change_24hr ?? 0) < 0
                      ? 'rgba(255, 0, 0, 0.02)' // Subtle red overlay
                      : 'transparent',
                pointerEvents: 'none', // Ensures the overlay doesn't interfere with interactions
              }}
            />

            <h4 className="text-lg font-semibold relative">Wallet Info</h4>

            <div className="flex items-center justify-center space-x-2 relative mt-2">
              <span
                className="text-sm text-gray-300 cursor-pointer"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                {walletKey}
              </span>

              {showTooltip && fullWalletKey && (
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-gray-700 text-white text-xs rounded-md px-2 py-1 shadow-md whitespace-nowrap">
                  {fullWalletKey}
                </div>
              )}

              <Button
                onClick={copyToClipboard}
                variant={'ghost'}
                className="bg-inherit ml-2 p-1 rounded relative z-20"
              >
                <img
                  src="/copy.svg"
                  alt="Copy"
                  className="w-4 h-4 filter invert brightness-0"
                />
              </Button>
            </div>

            <p className="text-sm mt-2">
              SOL Balance:{' '}
              <span className="font-bold">{walletData?.sol_balance}</span>
            </p>
            <p className="text-sm">
              USD Value:{' '}
              <span className="font-bold">
                ${walletData?.usd_value.toFixed(2)}
                <span
                  className={
                    (walletData?.percent_change_24hr ?? 0) > 0
                      ? 'text-green-500'
                      : (walletData?.percent_change_24hr ?? 0) < 0
                        ? 'text-red-500'
                        : 'text-white'
                  }
                >
                  ({(walletData?.percent_change_24hr ?? 0).toFixed(2)}%)
                </span>
              </span>
            </p>
          </HoverCardContent>
        </HoverCard>

        <div>
          <span
            onClick={() => navigate('/signals')}
            className="mr-4 text-base hover:underline cursor-pointer"
          >
            Signals
          </span>
          <span
            onClick={() => navigate('/order-history')}
            className="mr-4 text-base hover:underline cursor-pointer"
          >
            Order History
          </span>
          {/* <ManageModal /> */}
          <span
            onClick={() => navigate('/configure')}
            className="mr-4 text-base hover:underline cursor-pointer"
          >
            Configure
          </span>
          <Button
            variant="secondary"
            className="text-base hover:opacity-80"
            onClick={handleSendSol}
          >
            Send SOL
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Header
