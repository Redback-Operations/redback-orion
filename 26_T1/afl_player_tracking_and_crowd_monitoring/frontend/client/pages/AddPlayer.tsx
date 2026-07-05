import { useState } from "react";
import { useNavigate } from "react-router-dom";
import MobileNavigation from "@/components/MobileNavigation";
import { apiRequest } from "../lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Save, UserPlus } from "lucide-react";

export default function AddPlayer() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    team: "",
    position: "",
    photo: "",
    kicks: "0",
    handballs: "0",
    marks: "0",
    tackles: "0",
    goals: "0",
    efficiency: "75",
    age: "",
    height: "",
    weight: "",
    jerseyNumber: "",
    inside50s: "",
    disposals: "",
    teamLogo: "",
    notes: "",
  });

  const [errors, setErrors] = useState<{
    name?: string;
    team?: string;
    position?: string;
  }>({});

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [field]: "",
    }));

    setErrorMessage("");
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setFormData((prev) => ({
        ...prev,
        photo: reader.result as string,
      }));
    };
    reader.readAsDataURL(file);
  };

  const validateForm = () => {
    const newErrors: {
      name?: string;
      team?: string;
      position?: string;
    } = {};

    if (!formData.name.trim()) {
      newErrors.name = "Player name is required.";
    }

    if (!formData.team) {
      newErrors.team = "Please select a team.";
    }

    if (!formData.position) {
      newErrors.position = "Please select a position.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSavePlayer = async () => {
    setErrorMessage("");
    setSuccessMessage("");

    if (!validateForm()) return;

    setIsSaving(true);

    try {
      await apiRequest("http://localhost:8000/players", {
        method: "POST",
        body: JSON.stringify({
          name: formData.name,
          team: formData.team,
          position: formData.position,
          photo: formData.photo || "/players/dummy-player.png",
          kicks: Number(formData.kicks),
          handballs: Number(formData.handballs),
          marks: Number(formData.marks),
          tackles: Number(formData.tackles),
          goals: Number(formData.goals),
          efficiency: Number(formData.efficiency),
          age: Number(formData.age || 0),
          height: formData.height,
          weight: formData.weight,
          jerseyNumber: Number(formData.jerseyNumber || 0),
          inside50s: Number(formData.inside50s || 0),
          disposals: Number(formData.disposals || 0),
          teamLogo: formData.teamLogo,
          notes: formData.notes,
        }),
      });

      setSuccessMessage("Player added successfully.");
      console.log("Player added successfully");

      setTimeout(() => {
        navigate("/afl-dashboard");
      }, 800);
    } catch (err: any) {
      setErrorMessage(err.message || "Unable to save player.");
      console.error("Player save failed");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <MobileNavigation />

      <div className="lg:ml-64 min-h-screen flex flex-col">
        <div className="flex-1 px-4 md:px-6 py-6 flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Add New Player
              </h1>
              <p className="text-gray-600">
                Add a new player into the AFL analytics system
              </p>
            </div>

            <Button
              onClick={handleSavePlayer}
              disabled={isSaving}
              className="bg-green-600 hover:bg-green-700"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </div>

          <Card className="flex-1 w-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="w-5 h-5" />
                Player Details
              </CardTitle>
            </CardHeader>

            <CardContent className="flex-1 p-6 space-y-8 overflow-y-auto">
              {errorMessage && (
                <p className="text-sm text-red-500">{errorMessage}</p>
              )}

              {successMessage && (
                <p className="text-sm text-green-600">{successMessage}</p>
              )}

              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Basic Information
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <Label>Name</Label>
                    <Input
                      value={formData.name}
                      onChange={(e) => handleChange("name", e.target.value)}
                      placeholder="Enter player name"
                      className={
                        errors.name
                          ? "border-red-500 focus-visible:ring-red-500"
                          : ""
                      }
                    />
                    {errors.name && (
                      <p className="text-sm text-red-500">{errors.name}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Team</Label>
                    <Select
                      value={formData.team}
                      onValueChange={(value) => handleChange("team", value)}
                    >
                      <SelectTrigger
                        className={
                          errors.team ? "border-red-500 focus:ring-red-500" : ""
                        }
                      >
                        <SelectValue placeholder="Select team" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Western Bulldogs">
                          Western Bulldogs
                        </SelectItem>
                        <SelectItem value="Richmond">Richmond</SelectItem>
                        <SelectItem value="Geelong">Geelong</SelectItem>
                        <SelectItem value="Melbourne">Melbourne</SelectItem>
                        <SelectItem value="Carlton">Carlton</SelectItem>
                        <SelectItem value="Adelaide">Adelaide</SelectItem>
                        <SelectItem value="West Coast">West Coast</SelectItem>
                        <SelectItem value="Collingwood">Collingwood</SelectItem>
                        <SelectItem value="Essendon">Essendon</SelectItem>
                        <SelectItem value="Fremantle">Fremantle</SelectItem>
                        <SelectItem value="Brisbane">Brisbane</SelectItem>
                        <SelectItem value="Sydney">Sydney</SelectItem>
                        <SelectItem value="St Kilda">St Kilda</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.team && (
                      <p className="text-sm text-red-500">{errors.team}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Position</Label>
                    <Select
                      value={formData.position}
                      onValueChange={(value) => handleChange("position", value)}
                    >
                      <SelectTrigger
                        className={
                          errors.position
                            ? "border-red-500 focus:ring-red-500"
                            : ""
                        }
                      >
                        <SelectValue placeholder="Select position" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Midfielder">Midfielder</SelectItem>
                        <SelectItem value="Forward">Forward</SelectItem>
                        <SelectItem value="Defender">Defender</SelectItem>
                        <SelectItem value="Ruckman">Ruckman</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.position && (
                      <p className="text-sm text-red-500">{errors.position}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Player Photo</Label>
                    <Input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                    />
                    {formData.photo && (
                      <img
                        src={formData.photo}
                        alt="Preview"
                        className="w-24 h-24 rounded-full object-cover border shadow-sm mt-2"
                      />
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Age</Label>
                    <Input
                      type="number"
                      value={formData.age}
                      onChange={(e) => handleChange("age", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Height</Label>
                    <Input
                      value={formData.height}
                      onChange={(e) => handleChange("height", e.target.value)}
                      placeholder="e.g. 193 cm"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Weight</Label>
                    <Input
                      value={formData.weight}
                      onChange={(e) => handleChange("weight", e.target.value)}
                      placeholder="e.g. 93 kg"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Jersey Number</Label>
                    <Input
                      type="number"
                      value={formData.jerseyNumber}
                      onChange={(e) =>
                        handleChange("jerseyNumber", e.target.value)
                      }
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Performance Stats
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <Label>Kicks</Label>
                    <Input
                      type="number"
                      value={formData.kicks}
                      onChange={(e) => handleChange("kicks", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Handballs</Label>
                    <Input
                      type="number"
                      value={formData.handballs}
                      onChange={(e) =>
                        handleChange("handballs", e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Marks</Label>
                    <Input
                      type="number"
                      value={formData.marks}
                      onChange={(e) => handleChange("marks", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Tackles</Label>
                    <Input
                      type="number"
                      value={formData.tackles}
                      onChange={(e) => handleChange("tackles", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Goals</Label>
                    <Input
                      type="number"
                      value={formData.goals}
                      onChange={(e) => handleChange("goals", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Efficiency</Label>
                    <Input
                      type="number"
                      value={formData.efficiency}
                      onChange={(e) =>
                        handleChange("efficiency", e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Inside 50s</Label>
                    <Input
                      type="number"
                      value={formData.inside50s}
                      onChange={(e) =>
                        handleChange("inside50s", e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Disposals</Label>
                    <Input
                      type="number"
                      value={formData.disposals}
                      onChange={(e) =>
                        handleChange("disposals", e.target.value)
                      }
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Extra Details
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Input
                      value={formData.notes}
                      onChange={(e) => handleChange("notes", e.target.value)}
                      placeholder="Extra details"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
