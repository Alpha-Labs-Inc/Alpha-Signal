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

interface AutoSellConfig {
  sell_mode: string
  sell_type: string
  sell_value: number
  slippage: number
}

const AutoBuy = () => {
  const [autoSellStates, setAutoSellStates] = useState<AutoSellConfig>({
    sell_mode: '',
    sell_type: '',
    sell_value: 0,
    slippage: 0,
  })

  const getAutoSellConfig = async (): Promise<AutoSellConfig> => {
    const { data } = await axios.get('http://127.0.0.1:8000/config/auto-sell')
    setAutoSellStates(data)
    return data
  }

  const { data, isLoading } = useQuery({
    queryKey: ['get-auto-sell-config'],
    queryFn: getAutoSellConfig,
  })

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const saveAutoSellConfig = async (payload: AutoSellConfig): Promise<any> => {
    const { data } = await axios.post(
      'http://127.0.0.1:8000/config/auto-sell',
      {
        ...payload,
      }
    )
    return data
  }

  const mutation = useMutation({
    mutationFn: saveAutoSellConfig,
  })

  if (isLoading) return <Loader />

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
                  setAutoSellStates({
                    ...autoSellStates,
                    sell_type: e,
                  })
                }
                defaultValue={data?.sell_type}
              >
                <SelectTrigger className="w-[180px]">
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
            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Sell Mode</Label>
              <Select
                onValueChange={(e) =>
                  setAutoSellStates({
                    ...autoSellStates,
                    sell_mode: e,
                  })
                }
                defaultValue={data?.sell_mode}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select a Sell Mode" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="time_based">time_based</SelectItem>
                    <SelectItem value="stop_loss">stop_loss</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="m-2">Sell Value</Label>
              <input
                onChange={(e) =>
                  setAutoSellStates({
                    ...autoSellStates,
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
                  setAutoSellStates({
                    ...autoSellStates,
                    slippage: Number(e.target.value),
                  })
                }
                type="text"
                placeholder={JSON.stringify(data?.slippage)}
              />
            </div>
            <Button onClick={() => mutation.mutate(autoSellStates)}>
              Submit
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AutoBuy
