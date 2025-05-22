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
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { useToast } from '@/hooks/use-toast'
import { Trash2 } from "lucide-react"; // Import trashcan icon
import PlatformIcon from "./platform-icon";
import PlatformLinkButton from "./platform-link-button";

interface Profile {
    id: string;
    platform: string;
    username: string;
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

const createProfile = async (profileData: { platform: string, username: string }) => {
    const { data } = await axios.post("http://127.0.0.1:8000/profile", profileData);
    return data;
};

const ProfilesPage = () => {
    const { toast } = useToast()
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

    const createMutation = useMutation({
        mutationFn: createProfile,
        onSuccess: () => {
            toast({
                title: "Profile Created",
                description: "The profile has been successfully created.",
                duration: 2000,
            });
            refetch(); // Re-fetch profiles after creation
        },
    });

    const [platform, setPlatform] = useState("twitter");
    const [username, setUsername] = useState("");

    const handleCreateProfile = () => {
        createMutation.mutate({ platform, username });
    };

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>Error loading profiles.</p>;

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-center">
                    <CardTitle className="absolute left-1/2 transform -translate-x-1/2 text-lg font-bold">Trading Signals</CardTitle>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button className="ml-auto">Add Signal</Button>
                        </PopoverTrigger>
                        <PopoverContent className="space-y-4">
                            {/* Platform Selection */}
                            <div>
                                <Label>Platform</Label>
                                <Select onValueChange={setPlatform} defaultValue="twitter">
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Platform" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectGroup>
                                            <SelectItem value="twitter">Twitter</SelectItem>
                                            {/* Add more platforms as needed */}
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* username Input */}
                            <div>
                                <Label>username</Label>
                                <Input
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter Username"
                                />
                            </div>

                            {/* Create Button */}
                            <Button onClick={handleCreateProfile} className="mt-4">
                                Create
                            </Button>
                        </PopoverContent>
                    </Popover>
                </div>
            </CardHeader>
            <CardContent>
                <Accordion type="multiple" className="w-full">
                    {profiles?.map((profile) => {
                        const editableProfile = editedProfiles[profile.id] || profile;
                        return (
                            <AccordionItem key={profile.id} value={profile.id}>
                                <AccordionTrigger className="flex justify-between items-center p-4">
                                    <div className="flex items-center gap-4">
                                        <PlatformIcon platform={profile.platform} />
                                        <span className="font-bold text-lg">
                                            {profile.username}
                                        </span>
                                        <PlatformLinkButton platform={profile.platform} username={profile.username} />
                                    </div>
                                    <Badge
                                        variant={profile.is_active ? "success" : "destructive"}
                                        className="ml-auto mr-4"
                                    >
                                        {profile.is_active ? "Active" : "Inactive"}
                                    </Badge>
                                </AccordionTrigger>
                                <AccordionContent className="p-4 border-t">
                                    <div className="grid grid-cols-2 gap-4">
                                        {/* Buy Settings */}
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>AutoBuy Settings</CardTitle>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid grid-cols-1 gap-4">
                                                    <div>
                                                        <Label>Buy From</Label>
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
                                                        <Label>Buy Mode</Label>
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
                                                    <div className="relative">
                                                        <Label>
                                                            {editableProfile.buy_amount_type === "percent"
                                                                ? `Total % of ${editableProfile.buy_type} Spent per Buy`
                                                                : `Total ${editableProfile.buy_type} Spent per Buy`}
                                                        </Label>
                                                        <Input
                                                            type="number"
                                                            defaultValue={editableProfile.buy_amount}
                                                            placeholder={
                                                                editableProfile.buy_amount_type === "percent"
                                                                    ? "% (percentage)"
                                                                    : `Units (${editableProfile.buy_type})`
                                                            }
                                                            onChange={(e) =>
                                                                handleInputChange(profile.id, "buy_amount", Number(e.target.value))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <Label>Buy Slippage (%)</Label>
                                                        <Input
                                                            type="number"
                                                            defaultValue={(editableProfile.buy_slippage ?? 0) / 100} // Updated to handle undefined
                                                            onChange={(e) =>
                                                                handleInputChange(profile.id, "buy_slippage", Number(e.target.value) * 100)
                                                            }
                                                        />
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>


                                        {/* Sell Settings */}
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>AutoSell Settings</CardTitle>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid grid-cols-1 gap-4">
                                                    <div>
                                                        <Label>Sell To</Label>
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
                                                    <div className="flex flex-col items-center">
                                                        <Label className="text-center">
                                                            {editableProfile.sell_mode === "time_based"
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
                                                            defaultValue={editableProfile.sell_value}
                                                            placeholder={
                                                                editableProfile.sell_mode === "time_based"
                                                                    ? "Minutes"
                                                                    : "Percentage"
                                                            }
                                                            onChange={(e) =>
                                                                handleInputChange(profile.id, "sell_value", Number(e.target.value))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <Label>Sell Slippage (%)</Label>
                                                        <Input
                                                            type="number"
                                                            defaultValue={(editableProfile.sell_slippage ?? 0) / 100} // Updated to handle undefined
                                                            onChange={(e) =>
                                                                handleInputChange(profile.id, "sell_slippage", Number(e.target.value) * 100)
                                                            }
                                                        />
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
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
                                                            This will remove the username from the system.
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
