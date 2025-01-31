import { Button } from './ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

const ManageModal = () => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Manage</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage your wallet</DialogTitle>
          <DialogDescription>Temp text</DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="wallet" className="w-[600px]">
          <TabsList>
            <TabsTrigger value="wallet">Wallet Management</TabsTrigger>
            <TabsTrigger value="management">Token Management</TabsTrigger>
            <TabsTrigger value="swap">Token Swap</TabsTrigger>
          </TabsList>
          <TabsContent value="wallet">
            Make changes to your account here.
          </TabsContent>
          <TabsContent value="management">
            Change your password here.
          </TabsContent>
          <TabsContent value="swap">swap</TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}

export default ManageModal
