import ConfirmLogout from "@/components/ConfirmLogout";
import { useEffect, useState } from "react";
import { clearVideoState } from "@/lib/videoState";
import { useNavigate } from "react-router-dom";

import MobileNavigation from "@/components/MobileNavigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Activity,
  Camera,
  LogOut,
  Settings,
  User,
  Heart,
} from "lucide-react";

export default function Profile() {
  const navigate = useNavigate();

  // =====================================================
  // PROFILE STATE
  // =====================================================

  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [profileImage, setProfileImage] =
    useState<string | null>(null);

  // =====================================================
  // USER-SPECIFIC FAVOURITE STORAGE
  // =====================================================

  const getFavouriteStorageKey = (userEmail?: string) => {
    const resolvedEmail =
      userEmail || localStorage.getItem("userEmail") || "";

    if (!resolvedEmail.trim()) {
      return null;
    }

    return `favoritePlayers:${resolvedEmail
      .trim()
      .toLowerCase()}`;
  };

  // =====================================================
  // FAVOURITE PLAYERS STATE
  // =====================================================

  const [favoritePlayers, setFavoritePlayers] =
    useState<any[]>([]);

  // =====================================================
  // LOAD PROFILE + FAVOURITES
  // =====================================================

  useEffect(() => {
    const storedName =
      localStorage.getItem("userName") || "";

    const storedDob =
      localStorage.getItem("userDOB") || "";

    const storedEmail =
      localStorage.getItem("userEmail") || "";

    const storedRole =
      localStorage.getItem("userRole") || "";

    const storedImage =
      localStorage.getItem("userProfileImage");

    const storedOAuthUser =
      localStorage.getItem("oauthUser");

    let oauthProfileImage: string | null =
      null;

    if (storedOAuthUser) {
      try {
        const parsedOAuthUser =
          JSON.parse(storedOAuthUser);

        oauthProfileImage =
          parsedOAuthUser?.picture ||
          parsedOAuthUser?.photo ||
          parsedOAuthUser?.avatar ||
          null;
      } catch (error) {
        console.error(
          "Failed to parse OAuth user:",
          error
        );
      }
    }

    setName(storedName);
    setDob(storedDob);
    setEmail(storedEmail);
    setRole(storedRole);

    setProfileImage(
      storedImage ||
      oauthProfileImage ||
      null
    );

    // Load favourites belonging only to the current logged-in user.
    try {
      const favouriteKey =
        getFavouriteStorageKey(storedEmail);

      if (!favouriteKey) {
        setFavoritePlayers([]);
        return;
      }

      const storedFavorites = JSON.parse(
        localStorage.getItem(favouriteKey) || "[]"
      );

      setFavoritePlayers(
        Array.isArray(storedFavorites)
          ? storedFavorites
          : []
      );
    } catch (error) {
      console.error(
        "Failed to load favorite players:",
        error
      );

      setFavoritePlayers([]);
    }
  }, []);

  // =====================================================
  // PROFILE IMAGE CHANGE
  // =====================================================

  const handleImageChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onloadend = () => {
      const imageData = reader.result as string;

      setProfileImage(imageData);

      localStorage.setItem(
        "userProfileImage",
        imageData
      );
    };

    reader.readAsDataURL(file);
  };

  // =====================================================
  // SAVE PROFILE
  // =====================================================

  const handleSave = () => {
    localStorage.setItem("userName", name);
    localStorage.setItem("userDOB", dob);
    localStorage.setItem("userRole", role);

    if (profileImage) {
      localStorage.setItem(
        "userProfileImage",
        profileImage
      );
    }

    alert("Profile updated successfully");
  };

  // =====================================================
  // REMOVE FAVOURITE PLAYER
  // =====================================================

  const removeFavoritePlayer = (
    playerId: number
  ) => {
    const updatedFavorites =
      favoritePlayers.filter(
        (player) => player.id !== playerId
      );

    setFavoritePlayers(updatedFavorites);

    const favouriteKey =
      getFavouriteStorageKey(email);

    if (favouriteKey) {
      localStorage.setItem(
        favouriteKey,
        JSON.stringify(updatedFavorites)
      );
    }
  };

  // =====================================================
  // TEAM COLOURS
  // =====================================================

  const getTeamColor = (team: string) => {
    const teamColors: Record<string, string> = {
      "Western Bulldogs": "#1E40AF",
      Brisbane: "#8B0000",
      Richmond: "#FFD700",
      Geelong: "#1E3A8A",
      Melbourne: "#DC2626",
      Carlton: "#3B82F6",
      Adelaide: "#EF4444",
      "West Coast": "#1D4ED8",
      Collingwood: "#000000",
      Essendon: "#B91C1C",
      Fremantle: "#9333EA",
      Sydney: "#DC2626",
      "St Kilda": "#DC2626",
      "Port Adelaide": "#111827",
      "North Melbourne": "#2563EB",
      "Gold Coast": "#DC2626",
      "GWS Giants": "#F97316",
      Hawthorn: "#92400E",
    };

    return teamColors[team] || "#6B7280";
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    clearVideoState();
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("authToken");
    localStorage.removeItem("authProvider");
    localStorage.removeItem("userProfileImage");
    localStorage.removeItem("oauthUser");

    sessionStorage.removeItem("isAuthenticated");
    sessionStorage.removeItem("userEmail");
    sessionStorage.removeItem("userName");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    sessionStorage.removeItem("authToken");
    sessionStorage.removeItem("authProvider");

    navigate("/login", {
      replace: true,
    });
  };

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-20 lg:pb-0">



        {/* =================================================
            PROFILE CONTENT
        ================================================= */}

        <main className="px-4 sm:px-6 py-6">

          {/* Page Title */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              My Profile
            </h1>

            <p className="mt-1 text-gray-600">
              Manage your personal information
            </p>
          </div>

          {/* =================================================
              PROFILE INFORMATION CARD
          ================================================= */}

          <Card className="max-w-4xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Profile Information
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-8">

              {/* Profile Image */}
              <div className="flex flex-col sm:flex-row sm:items-center gap-5">
                <div className="relative w-fit">

                  {profileImage ? (
                    <img
                      src={profileImage}
                      alt="Profile"
                      className="h-28 w-28 rounded-full object-cover border-4 border-white shadow"
                      onError={(event) => {
                        console.error(
                          "Profile image failed to load:",
                          profileImage
                        );

                        event.currentTarget.style.display =
                          "none";
                      }}
                    />
                  ) : (
                    <div className="h-28 w-28 rounded-full bg-gray-100 border flex items-center justify-center">
                      <User className="h-12 w-12 text-gray-400" />
                    </div>
                  )}

                  <label className="absolute bottom-0 right-0 cursor-pointer rounded-full bg-green-600 p-2.5 text-white shadow-md hover:bg-green-700 transition-colors">
                    <Camera className="h-4 w-4" />

                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleImageChange}
                    />
                  </label>
                </div>

                <div>
                  <h3 className="font-semibold text-lg">
                    Profile Photo
                  </h3>

                  <p className="text-sm text-gray-500">
                    Upload or update your profile picture
                  </p>
                </div>
              </div>

              <div className="border-t" />

              {/* Profile Form */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Full Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">
                    Full Name
                  </Label>

                  <Input
                    id="name"
                    value={name}
                    onChange={(e) =>
                      setName(e.target.value)
                    }
                    placeholder="Enter your full name"
                  />
                </div>

                {/* Date of Birth */}
                <div className="space-y-2">
                  <Label htmlFor="dob">
                    Date of Birth
                  </Label>

                  <Input
                    id="dob"
                    type="date"
                    value={dob}
                    onChange={(e) =>
                      setDob(e.target.value)
                    }
                  />
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <Label htmlFor="email">
                    Email Address
                  </Label>

                  <Input
                    id="email"
                    value={email}
                    disabled
                    className="bg-gray-100 cursor-not-allowed"
                  />

                  <p className="text-xs text-gray-500">
                    Your login email cannot be edited
                  </p>
                </div>

                
              </div>

              <div className="border-t" />

              {/* Save */}
              <div className="flex justify-end">
                <Button
                  onClick={handleSave}
                  className="min-w-36 bg-green-600 hover:bg-green-700"
                >
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* =================================================
              FAVOURITE PLAYERS CARD
          ================================================= */}

          <Card className="max-w-4xl mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5 fill-red-500 text-red-500" />
                Favourite Players
              </CardTitle>

              <p className="text-sm text-gray-500">
                Players you selected from the Player Performance page
              </p>
            </CardHeader>

            <CardContent>

              {/* No Favourites */}
              {favoritePlayers.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-center">

                  <Heart className="mb-3 h-10 w-10 text-gray-300" />

                  <h3 className="font-semibold text-gray-700">
                    No favourite players yet
                  </h3>

                  <p className="mt-1 text-sm text-gray-500 max-w-md">
                    Go to the Player Performance page and click the heart icon
                    on any player card to add that player to your favourites.
                  </p>

                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() =>
                      navigate("/player-performance")
                    }
                  >
                    Browse Players
                  </Button>
                </div>
              ) : (

                /* Favourite Player Grid */
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                  {favoritePlayers.map((player) => (
                    <div
                      key={player.id}
                      className="overflow-hidden rounded-xl border bg-white shadow-sm transition-all duration-200 hover:shadow-md"
                    >

                      {/* Team Header */}
                      <div
                        className="relative h-20 px-4 text-white"
                        style={{
                          backgroundColor:
                            getTeamColor(player.team),
                        }}
                      >
                        <div className="absolute left-4 top-3">
                          <div className="text-xl font-bold">
                            #{player.number}
                          </div>

                          <div className="text-sm">
                            {player.team}
                          </div>
                        </div>

                        <div className="absolute right-4 top-3 text-right">
                          <div className="text-xl font-bold">
                            {player.stats?.disposals ?? 0}
                          </div>

                          <div className="text-xs">
                            DISPOSALS
                          </div>
                        </div>
                      </div>

                      {/* Player Details */}
                      <div className="p-4">

                        <div className="flex items-center gap-3 mb-4">

                          {/* Player Photo */}
                          {player.photo ? (
                            <img
                              src={player.photo}
                              alt={player.name}
                              className="w-12 h-12 rounded-full object-cover border"
                            />
                          ) : (
                            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                              <User className="w-6 h-6 text-gray-400" />
                            </div>
                          )}

                          {/* Name */}
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold truncate">
                              {player.name}
                            </h3>

                            <p className="text-sm text-gray-500">
                              {player.position}
                            </p>
                          </div>

                          {/* Remove Favourite */}
                          <button
                            type="button"
                            onClick={() =>
                              removeFavoritePlayer(player.id)
                            }
                            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:scale-110 hover:bg-red-50"
                            title="Remove from favourites"
                            aria-label={`Remove ${player.name} from favourites`}
                          >
                            <Heart className="h-5 w-5 fill-red-500 text-red-500" />
                          </button>
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-2 text-center text-xs">

                          {/* Goals */}
                          <div className="rounded bg-blue-50 p-2">
                            <div className="font-bold text-blue-600">
                              {player.stats?.goals ?? 0}
                            </div>

                            <div className="text-gray-600">
                              Goals
                            </div>
                          </div>

                          {/* Marks */}
                          <div className="rounded bg-green-50 p-2">
                            <div className="font-bold text-green-600">
                              {player.stats?.marks ?? 0}
                            </div>

                            <div className="text-gray-600">
                              Marks
                            </div>
                          </div>

                          {/* Efficiency */}
                          <div className="rounded bg-purple-50 p-2">
                            <div className="font-bold text-purple-600">
                              {player.stats?.efficiency ?? 0}%
                            </div>

                            <div className="text-gray-600">
                              Eff.
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}