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
import { Popover, PopoverTrigger, PopoverContent } from './ui/popover'

interface AutoSellConfig {
  sell_mode: string
  sell_type: string
  sell_value: number
  slippage: number
}

const AutoSell = () => {
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
    toast({
      title: 'Configuration Updated',
      description: `The auto sell configuration has been successfully updated.`,
      duration: 2000,
    })
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
            <div className="my-4 flex flex-col justify-center items-start w-full">
              <Label className="m-2">Sell To</Label>
              <Select
                onValueChange={(e) =>
                  setAutoSellStates({
                    ...autoSellStates,
                    sell_type: e,
                  })
                }
                defaultValue={data?.sell_type}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a Sell Type" />
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
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a Sell Mode" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="time_based">Time Based</SelectItem>
                    <SelectItem value="stop_loss">Stop Loss</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="my-4 flex flex-col justify-center items-start">
              <Label className="text-center mb-2">
                {autoSellStates.sell_mode === "time_based"
                  ? "Total Minutes Until Sell"
                  : (
                      <div className="flex items-center justify-center">
                        Rolling Stop Loss % to Sell
                        <Popover>
                          <PopoverTrigger asChild>
                            <span className="ml-2 text-gray-500 cursor-pointer">ⓘ</span>
                          </PopoverTrigger>
                          <PopoverContent>
                            This is the percentage drop from the highest price *after* token purchase that will trigger a sell, i.e. the stop-loss price moves up as price does.<br/><br/>This allows for stop losses that protect your downside while also locking in the upside.
                          </PopoverContent>
                        </Popover>
                      </div>
                  )}
              </Label>
              <Input
                type="number"
                defaultValue={JSON.stringify(data?.sell_value)}
                placeholder={
                  autoSellStates.sell_mode === "time_based"
                    ? "Minutes"
                    : "Percentage"
                }
                onChange={(e) =>
                  setAutoSellStates({
                    ...autoSellStates,
                    sell_value: Number(e.target.value),
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
                  setAutoSellStates({
                    ...autoSellStates,
                    slippage: Number(e.target.value) * 100,
                  })
                }
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

export default AutoSell
