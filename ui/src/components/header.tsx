import { HoverCard, HoverCardContent, HoverCardTrigger } from './ui/hover-card'
import ManageModal from './manage-modal'
import { useNavigate } from 'react-router-dom'

const Header = () => {
  const navigate = useNavigate()
  return (
    <div className="w-full flex justify-between items-center w-100">
      <HoverCard>
        <HoverCardTrigger asChild className="flex items-center space-x-2">
          <span
            onClick={() => navigate('/')}
            className=" text-3xl hover:underline cursor-pointer font-bold"
          >
            Alpha Signal
          </span>
        </HoverCardTrigger>
        <HoverCardContent className="w-80">
          <div className="flex justify-between space-x-4">
            <div className="space-y-1">
              <h4 className="text-sm font-semibold">Alpha Labs Inc</h4>
              <p className="text-sm">
                AI Algorithmic Trading for the Blockchain
              </p>
              <div className="flex items-center pt-2">
                <span className="text-xs text-muted-foreground">
                  Find us at @AlphaSignalCrypto on X
                </span>
              </div>
            </div>
          </div>
        </HoverCardContent>
      </HoverCard>
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
  )
}
export default Header
