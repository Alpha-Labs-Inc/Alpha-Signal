import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";

interface WalletToken {
  name: string;
  mint_address: string;
  balance: number;
  value: number;
}

const TableView = () => {
  const [walletTokens, setWalletTokens] = useState<WalletToken[]>([]);
  const [totalValue, setTotalValue] = useState(0);

  useEffect(() => {
    const fetchWalletData = async () => {
      try {
        const response = await fetch("http://localhost:8000/wallet-value");
        if (!response.ok) throw new Error("Failed to fetch wallet data");

        const data: { wallet_tokens: WalletToken[]; total_value: number } = await response.json();
        setWalletTokens(data.wallet_tokens || []);
        setTotalValue(data.total_value || 0);
      } catch (error) {
        console.error("Error fetching wallet data:", error);
      }
    };

    fetchWalletData();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wallet</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableCaption>A list of your holdings</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Token Name</TableHead>
              <TableHead>Mint Address</TableHead>
              <TableHead>Balance</TableHead>
              <TableHead className="text-right">Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {walletTokens.length > 0 ? (
              walletTokens.map((token, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium text-left">
                    {token.name}
                  </TableCell>
                  <TableCell className="text-left">
                    {token.mint_address}
                  </TableCell>
                  <TableCell className="text-left">{token.balance}</TableCell>
                  <TableCell className="text-right">
                    ${token.value.toFixed(2)}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} className="text-center">
                  No tokens found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <div className="text-right font-bold mt-4">
          Total Wallet Value: ${totalValue.toFixed(2)}
        </div>
      </CardContent>
    </Card>
  );
};

export default TableView;
