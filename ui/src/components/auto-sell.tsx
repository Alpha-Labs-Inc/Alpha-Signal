import axios from 'axios'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Label } from './ui/label'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from './ui/select'
import { useState } from 'react'
import { Button } from './ui/button'

interface AutoBuyConfig {
  sell_mode: string
  sell_type: string
  sell_value: number
  slippage: number
}

const AutoBuy = () => {
  const [autoBuyStates, setAutoBuyStates] = useState<AutoBuyConfig>({
    sell_mode: '',
    sell_type: '',
    sell_value: 0,
    slippage: 0,
  })

  const getAutoBuyConfig = async (): Promise<AutoBuyConfig> => {
    const { data } = await axios.get('http://127.0.0.1:8000/config/auto-sell')
    return data.orders
  }

  const { data } = useQuery({
    queryKey: ['get-auto-buy-config'],
    queryFn: getAutoBuyConfig,
  })

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const saveAutoBuyConfig = async (payload: AutoBuyConfig): Promise<any> => {
    const { data } = await axios.post(
      'http://127.0.0.1:8000/config/auto-sell',
      {
        ...payload,
      }
    )
    return data.orders
  }

  const mutation = useMutation({
    mutationFn: saveAutoBuyConfig,
  })

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Auto Sell Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Sell Type</Label>
              <Select
                onValueChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    sell_type: e,
                  })
                }
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select a Buy Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Buy Type</SelectLabel>
                    <SelectItem value="USDC">USDC</SelectItem>
                    <SelectItem value="SOL">SOL</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Sell Type</Label>
              <Select
                onValueChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    sell_type: e,
                  })
                }
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select a Amount Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Amount Type</SelectLabel>
                    <SelectItem value="percent">percent</SelectItem>
                    <SelectItem value="amount">amount</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Sell Value</Label>
              <input
                onChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    sell_value: Number(e.target.value),
                  })
                }
                type="text"
                placeholder={JSON.stringify(data?.sell_value)}
              />
            </div>
            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Slippage</Label>
              <input
                onChange={(e) =>
                  setAutoBuyStates({
                    ...autoBuyStates,
                    slippage: Number(e.target.value),
                  })
                }
                type="text"
                placeholder={JSON.stringify(data?.slippage)}
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
