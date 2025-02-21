import axios from 'axios'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Label } from './ui/label'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'
import { useState } from 'react'
import { Button } from './ui/button'
import Loader from './loader'
import { toast } from '@/hooks/use-toast'
import { Input } from './ui/input'

interface AutoBuyConfig {
  buy_type: string
  amount_type: string
  amount: number
  slippage: number
}

const AutoBuy = () => {
  const [autoBuyStates, setAutoBuyStates] = useState<AutoBuyConfig>({
    buy_type: '',
    amount_type: '',
    amount: 0,
    slippage: 0,
  })

  const getAutoBuyConfig = async (): Promise<AutoBuyConfig> => {
    const { data } = await axios.get('http://127.0.0.1:8000/config/auto-buy')
    setAutoBuyStates(data)
    return data
  }

  const { data, isLoading } = useQuery({
    queryKey: ['get-auto-buy-config'],
    queryFn: getAutoBuyConfig,
  })

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const saveAutoBuyConfig = async (payload: AutoBuyConfig): Promise<any> => {
    const { data } = await axios.post('http://127.0.0.1:8000/config/auto-buy', {
      ...payload,
    })
    toast({
      title: 'Configuration Updated',
      description: `The auto buy configuration has been successfully updated.`,
      duration: 2000,
    })
    return data
  }

  const mutation = useMutation({
    mutationFn: saveAutoBuyConfig,
  })

  if (isLoading) return <Loader />

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Auto Buy Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <div className="my-4 flex flex-col justify-center items-start w-full">
              <Label className="m-2">Buy From</Label>
              <Select
                onValueChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    buy_type: e,
                  })
                }
                defaultValue={data?.buy_type}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a Buy Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="USDC">USDC</SelectItem>
                    <SelectItem value="SOL">SOL</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="my-4 flex flex-col justify-center items-start w-full">
              <Label className="m-2">Amount Type</Label>
              <Select
                onValueChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    amount_type: e,
                  })
                }
                defaultValue={data?.amount_type}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select an Amount Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="percent">Percent</SelectItem>
                    <SelectItem value="amount">Amount</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="text-center mb-2">
                {autoBuyStates.amount_type === "percent"
                  ? "Total % of Buy Type Spent per Buy"
                  : `Total ${autoBuyStates.buy_type} Spent per Buy`}
              </Label>
              <Input
                type="number"
                defaultValue={JSON.stringify(data?.amount)}
                placeholder={
                  autoBuyStates.amount_type === "percent"
                    ? "% (percentage)"
                    : `Units (${autoBuyStates.buy_type})`
                }
                onChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    amount: Number(e.target.value),
                  })
                }
              />
            </div>
            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Slippage (%)</Label>
              <Input
                type="number"
                defaultValue={JSON.stringify(data ? data.slippage / 100 : 0)}
                onChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    slippage: Number(e.target.value) * 100,
                  })
                }
              />
            </div>
            <Button onClick={() => mutation.mutate(autoBuyStates)}>
              Submit
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AutoBuy
