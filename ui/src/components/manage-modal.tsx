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
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { useToast } from '@/hooks/use-toast'

const ManageModal = () => {
  const { toast } = useToast()
  const FormSchema = z.object({
    fundPrivateKey: z.string().min(2, {
      message: 'PrivateKey must be at least 2 characters.',
    }),
    amount: z
      .string()
      .refine((val) => !isNaN(parseFloat(val)) && parseFloat(val) > 0, {
        message: 'Amount must be a number greater than 0.',
      }),
  })

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      fundPrivateKey: '',
      amount: '0', // Default value as string
    },
  })

  const addFunds = async (data: {
    funding_private_key: string
    amt: number
  }) => {
    const response = await axios.post('http://localhost:8000/add-funds', {
      ...data,
    })
    return response.data
  }

  const mutation = useMutation({
    mutationFn: addFunds,
    onSuccess: () => {
      toast({ title: 'Success', description: 'Funds successfully added' })
    },
    onError: () =>
      toast({ title: 'Error', description: 'Failed to add funds' }),
  })

  function onSubmit(data: z.infer<typeof FormSchema>) {
    mutation.mutate({
      funding_private_key: data.fundPrivateKey,
      amt: parseFloat(data.amount), // Convert amount to number
    })
  }

  const onReset = () => form.reset()

  const addFundsNode = (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
        <FormField
          control={form.control}
          name="fundPrivateKey"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Funding private key</FormLabel>
              <FormControl>
                <Input placeholder="Enter Private Key" {...field} />
              </FormControl>
              <FormDescription>We wont steal your keys</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="amount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Amount</FormLabel>
              <FormControl>
                <Input type="text" placeholder="$0" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex space-x-4">
          <Button type="submit">Submit</Button>
          <Button type="button" onClick={onReset}>
            Clear
          </Button>
        </div>
      </form>
    </Form>
  )

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Manage</Button>
      </DialogTrigger>
      <DialogContent className="min-h-[400px] min-w-max flex flex-col">
        <DialogHeader>
          <DialogTitle>Manage your wallet</DialogTitle>
          {/* todo replace this text later */}
          <DialogDescription>Temp text</DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="add-funds" className="w-[600px]">
          <TabsList>
            <TabsTrigger value="add-funds">Add Funds</TabsTrigger>
            <TabsTrigger value="management">Token Management</TabsTrigger>
            <TabsTrigger value="swap">Token Swap</TabsTrigger>
            <TabsTrigger value="wallet">Wallet Management</TabsTrigger>
          </TabsList>

          <TabsContent value="add-funds">{addFundsNode}</TabsContent>
          <TabsContent value="wallet">wallet stuff</TabsContent>
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
