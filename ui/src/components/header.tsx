import { HoverCard, HoverCardContent, HoverCardTrigger } from './ui/hover-card'
import { Avatar, AvatarImage } from './ui/avatar'
import ManageModal from './manage-modal'

const Header = () => {
  return (
    <div className="w-full flex justify-between items-center w-100">
      <HoverCard>
        <HoverCardTrigger asChild className="flex items-center space-x-2">
          <span className=" text-lg font-medium hover:underline cursor-pointer">
            Alpha-Sigma
            <Avatar>
              <AvatarImage src="../assets/logo.jpg" alt="logo" />
            </Avatar>
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
                  Find us at @alphasigma on X
                </span>
              </div>
            </div>
          </div>
        </HoverCardContent>
      </HoverCard>
      <ManageModal />
    </div>
  )
}
export default Header
