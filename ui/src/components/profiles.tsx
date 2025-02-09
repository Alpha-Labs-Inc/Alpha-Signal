import axios from "axios";
import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Accordion,
    AccordionItem,
    AccordionTrigger,
    AccordionContent,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectGroup, SelectItem } from "@/components/ui/select";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { Trash2 } from "lucide-react"; // Import trashcan icon

interface Profile {
    id: string;
    platform: string;
    signal: string;
    is_active: boolean;
    buy_type: string;
    buy_amount_type: string;
    buy_amount: number;
    buy_slippage: number;
    sell_mode: string;
    sell_type: string;
    sell_value: number;
    sell_slippage: number;
}


const deleteProfile = async (profileId: string) => {
    await axios.delete(`http://127.0.0.1:8000/profile/${profileId}`);
};


const activateProfile = async (profileId: string) => {
    await axios.patch(`http://127.0.0.1:8000/profile/${profileId}/activate`);
};

const deactivateProfile = async (profileId: string) => {
    await axios.patch(`http://127.0.0.1:8000/profile/${profileId}/deactivate`);
};


const updateProfile = async ({ profileId, updatedData }: { profileId: string; updatedData: Partial<Profile> }) => {
    await axios.put(`http://127.0.0.1:8000/profile/${profileId}`, updatedData);
};

const ProfilesPage = () => {

    const fetchProfiles = async (): Promise<Profile[]> => {
        const { data } = await axios.get("http://127.0.0.1:8000/profiles");

        // Initialize state for each profile to ensure all fields are set
        setEditedProfiles((prev) => {
            const newProfiles = { ...prev };
            data.forEach((profile: Profile) => {
                if (!newProfiles[profile.id]) {
                    newProfiles[profile.id] = { ...profile }; // Ensure defaults are set
                }
            });
            return newProfiles;
        });

        return data;
    };

    const { data: profiles, isLoading, error, refetch } = useQuery({
        queryKey: ["profiles"],
        queryFn: fetchProfiles,
    });

    const mutation = useMutation({
        mutationFn: updateProfile,
        onSuccess: () => {
            toast({
                title: "Profile Updated",
                description: "The profile settings have been successfully updated.",
                duration: 2000,
            });
            refetch();
        },
    });

    const [editedProfiles, setEditedProfiles] = useState<{ [key: string]: Partial<Profile> }>({});

    const handleInputChange = (id: string, field: keyof Profile, value: string | number) => {
        setEditedProfiles((prev) => ({
            ...prev,
            [id]: {
                ...prev[id],
                [field]: value,
            },
        }));
    };

    const handleUpdate = (profileId: string) => {
        if (!editedProfiles[profileId]) return;
        mutation.mutate({ profileId, updatedData: editedProfiles[profileId] });
    };

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>Error loading profiles.</p>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Trading Signals</CardTitle>
            </CardHeader>
            <CardContent>
                <Accordion type="multiple" className="w-full">
                    {profiles?.map((profile) => {
                        const editableProfile = profile;
                        return (
                            <AccordionItem key={profile.id} value={profile.id}>
                                <AccordionTrigger className="flex justify-between items-center p-4">
                                    <div className="flex gap-4">
                                        <span className="font-semibold">{profile.platform}</span>
                                        <span>{profile.signal}</span>
                                    </div>
                                    <Badge
                                        variant={profile.is_active ? "success" : "destructive"}
                                        className="ml-auto"
                                    >
                                        {profile.is_active ? "Active" : "Inactive"}
                                    </Badge>
                                </AccordionTrigger>
                                <AccordionContent className="p-4 border-t">
                                    <div className="grid grid-cols-2 gap-4">
                                        {/* Buy Settings */}
                                        <div>
                                            <Label>Buy Type</Label>
                                            <Select
                                                onValueChange={(e) => handleInputChange(profile.id, "buy_type", e)}
                                                defaultValue={editableProfile.buy_type}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select Buy Type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectGroup>
                                                        <SelectItem value="USDC">USDC</SelectItem>
                                                        <SelectItem value="SOL">SOL</SelectItem>
                                                    </SelectGroup>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div>
                                            <Label>Buy Amount Type</Label>
                                            <Select
                                                onValueChange={(e) => handleInputChange(profile.id, "buy_amount_type", e)}
                                                defaultValue={editableProfile.buy_amount_type}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select Amount Type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectGroup>
                                                        <SelectItem value="percent">Percent</SelectItem>
                                                        <SelectItem value="amount">Amount</SelectItem>
                                                    </SelectGroup>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div>
                                            <Label>Buy Amount</Label>
                                            <Input
                                                type="number"
                                                defaultValue={editableProfile.buy_amount}
                                                onChange={(e) =>
                                                    handleInputChange(profile.id, "buy_amount", Number(e.target.value))
                                                }
                                            />
                                        </div>
                                        <div>
                                            <Label>Buy Slippage (%)</Label>
                                            <Input
                                                type="number"
                                                defaultValue={editableProfile.buy_slippage}
                                                onChange={(e) =>
                                                    handleInputChange(profile.id, "buy_slippage", Number(e.target.value))
                                                }
                                            />
                                        </div>

                                        {/* Sell Settings */}
                                        <div>
                                            <Label>Sell Mode</Label>
                                            <Select
                                                onValueChange={(e) => handleInputChange(profile.id, "sell_mode", e)}
                                                defaultValue={editableProfile.sell_mode}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select Sell Mode" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectGroup>
                                                        <SelectItem value="time_based">Time Based</SelectItem>
                                                        <SelectItem value="stop_loss">Stop Loss</SelectItem>
                                                    </SelectGroup>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div>
                                            <Label>Sell Type</Label>
                                            <Select
                                                onValueChange={(e) => handleInputChange(profile.id, "sell_type", e)}
                                                defaultValue={editableProfile.sell_type}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select Sell Type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectGroup>
                                                        <SelectItem value="USDC">USDC</SelectItem>
                                                        <SelectItem value="SOL">SOL</SelectItem>
                                                    </SelectGroup>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div>
                                            <Label>Sell Value</Label>
                                            <Input
                                                type="number"
                                                defaultValue={editableProfile.sell_value}
                                                onChange={(e) =>
                                                    handleInputChange(profile.id, "sell_value", Number(e.target.value))
                                                }
                                            />
                                        </div>
                                        <div>
                                            <Label>Sell Slippage (%)</Label>
                                            <Input
                                                type="number"
                                                defaultValue={editableProfile.sell_slippage}
                                                onChange={(e) =>
                                                    handleInputChange(profile.id, "sell_slippage", Number(e.target.value))
                                                }
                                            />
                                        </div>
                                    </div>


                                    <div className="flex justify-between items-center mt-4">
                                        <Button
                                            variant={editableProfile.is_active ? "destructive" : "success"}
                                            onClick={() => {
                                                if (editableProfile.is_active) {
                                                    deactivateProfile(profile.id).then(() => refetch());
                                                } else {
                                                    activateProfile(profile.id).then(() => refetch());
                                                }
                                            }}
                                        >
                                            {editableProfile.is_active ? "Deactivate" : "Activate"}
                                        </Button>

                                        <div className="flex justify-end gap-2 mt-4">
                                            <Button onClick={() => handleUpdate(profile.id)}>Update</Button>
                                            <AlertDialog>
                                                <AlertDialogTrigger asChild>
                                                    <Button variant="destructive">
                                                        <Trash2 className="w-5 h-5" />
                                                    </Button>
                                                </AlertDialogTrigger>
                                                <AlertDialogContent>
                                                    <AlertDialogHeader>
                                                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                                                        <AlertDialogDescription>
                                                            This will remove the signal from the system.
                                                        </AlertDialogDescription>
                                                    </AlertDialogHeader>
                                                    <AlertDialogFooter>
                                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                        <AlertDialogAction className='destructive'
                                                            onClick={() => {
                                                                deleteProfile(profile.id).then(() => refetch());
                                                            }}>Delete</AlertDialogAction>
                                                    </AlertDialogFooter>
                                                </AlertDialogContent>
                                            </AlertDialog>
                                        </div>

                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                        );
                    })}
                </Accordion>
            </CardContent>
        </Card>
    );
};

export default ProfilesPage;
