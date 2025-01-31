import { toast } from '@/hooks/use-toast'
import { Button } from './ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from './ui/form'
import { Input } from './ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

const ManageModal = () => {
  const FormSchema = z.object({
    username: z.string().min(2, {
      message: 'Username must be at least 2 characters.',
    }),
  })

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      username: '',
    },
  })

  function onSubmit(data: z.infer<typeof FormSchema>) {
    toast({
      title: 'You submitted the following values:',
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    })
  }

  const walletTab = (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Manage</Button>
      </DialogTrigger>
      <DialogContent className="   min-h-[400px]">
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
          <TabsContent value="wallet">{walletTab}</TabsContent>
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
