import { useState, useEffect } from 'react';
import { HoverCard, HoverCardContent, HoverCardTrigger } from './ui/hover-card';
import { Avatar, AvatarImage } from './ui/avatar';
import { ClipboardCopy } from 'lucide-react';
import ManageModal from './manage-modal';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const [walletData, setWalletData] = useState<{ sol_balance: number; usd_value: number } | null>(null);
  const [walletKey, setWalletKey] = useState<string | null>(null);
  const [fullWalletKey, setFullWalletKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false); // Tooltip visibility

  useEffect(() => {
    const fetchWalletKey = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/load-wallet');
        if (data?.public_key) {
          setFullWalletKey(data.public_key);
          setWalletKey(`${data.public_key.slice(0, 3)}...${data.public_key.slice(-3)}`);
        } else {
          setWalletKey('N/A');
        }
      } catch (error) {
        console.error('Error fetching wallet key:', error);
        setWalletKey('Error');
      }
    };

    const fetchSolValue = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/sol-value');
        if (data?.sol_balance !== undefined && data?.usd_value !== undefined) {
          setWalletData({
            sol_balance: data.sol_balance,
            usd_value: data.usd_value,
          });
        } else {
          setWalletData({ sol_balance: 0, usd_value: 0 });
        }
      } catch (error) {
        console.error('Error fetching SOL value:', error);
        setWalletData({ sol_balance: 0, usd_value: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchWalletKey();
    fetchSolValue();
  }, []);

  const copyToClipboard = () => {
    if (fullWalletKey) {
      navigator.clipboard.writeText(fullWalletKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const navigate = useNavigate()
  return (
    <div className="w-full flex justify-between items-center px-4 py-3">
      {/* Alpha Signal Logo & Hover */}
      <HoverCard>
        <HoverCardTrigger asChild className="flex items-center space-x-2 cursor-pointer">
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
              Find us at @AlphaSignalCrypto on X
            </span>
          </div>
        </HoverCardContent>
      </HoverCard>

      {/* Right-Aligned Wallet Button & Manage Modal */}
      <div className="ml-auto flex items-center space-x-4">
        <HoverCard>
          <HoverCardTrigger asChild>
            <div className="px-6 py-2 bg-white text-black text-center rounded-md cursor-pointer shadow-md border border-gray-300 hover:bg-gray-100 transition w-[120px] h-[40px] flex items-center justify-center">
              Wallet
            </div>
          </HoverCardTrigger>
          <HoverCardContent className="w-64 p-4 border rounded-lg shadow-md bg-gray-900 text-white text-center">
            <h4 className="text-lg font-semibold">Wallet Info</h4>

            {/* Wallet Key Section with Custom Tooltip */}
            <div className="flex items-center justify-center space-x-2 relative mt-2">
              <span
                className="text-sm text-gray-300 cursor-pointer"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                {walletKey}
              </span>

              {/* Tooltip that shows full wallet key */}
              {showTooltip && fullWalletKey && (
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-gray-700 text-white text-xs rounded-md px-2 py-1 shadow-md whitespace-nowrap">
                  {fullWalletKey}
                </div>
              )}

              {/* Copy Button */}
              <button
                onClick={copyToClipboard}
                className="p-1 bg-gray-700 rounded-md hover:bg-gray-600 transition"
              >
                <ClipboardCopy size={16} className={copied ? 'text-green-500' : 'text-white'} />
              </button>
            </div>

            <p className="text-sm mt-2">
              SOL Balance: <span className="font-bold">{walletData?.sol_balance.toFixed(2)}</span>
            </p>
            <p className="text-sm">
              USD Value: <span className="font-bold">${walletData?.usd_value.toFixed(2)}</span>
            </p>
          </HoverCardContent>
        </HoverCard>

        {/* Manage Modal Button (same size as Wallet) */}
        <div className="w-[120px] h-[40px] flex items-center justify-center">
          <div>
            <span
              onClick={() => navigate('/order-history')}
              className=" mr-4 text-base hover:underline cursor-pointer "
            >
              Order History
            </span>
            <ManageModal />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
