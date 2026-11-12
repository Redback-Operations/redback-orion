import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import MobileNavigation from "@/components/MobileNavigation";
import { apiRequest } from "@/lib/api";
import { AuthUser } from "@/lib/auth";

const API_BASE_URL = "http://localhost:8000";

interface BackendPlayer {
  id: number;
  name: string;
  team: string;
  jersey_number: number;
}

export default function Admin() {
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Password reset state
  const [resettingUserId, setResettingUserId] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [resetStatus, setResetStatus] = useState<Record<string, string>>({});

  // Create Player/Coach account state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [availablePlayers, setAvailablePlayers] = useState<BackendPlayer[]>([]);
  const [createForm, setCreateForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "coach", // "player" or "coach"
    player_id: "",
  });
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const fetchUsers = () => {
    setLoading(true);
    setError("");
    apiRequest(`${API_BASE_URL}/auth/users`)
      .then((data) => setUsers(data.users || []))
      .catch((err) => setError(err.message || "Failed to load users"))
      .finally(() => setLoading(false));
  };

  const fetchAvailablePlayers = () => {
    apiRequest(`${API_BASE_URL}/api/players`)
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        setAvailablePlayers(list);
      })
      .catch(() => {
        // non-fatal — the player dropdown will just be empty
      });
  };

  useEffect(() => {
    fetchUsers();
    fetchAvailablePlayers();
  }, []);

  const handleRoleChange = async (userId: string, newRole: string) => {
    // optimistic update
    const previous = users;
    setUsers((prev) =>
      prev.map((u) => (u.user_id === userId ? { ...u, role: newRole as any } : u)),
    );

    try {
      await apiRequest(`${API_BASE_URL}/auth/users/${userId}/role`, {
        method: "PUT",
        body: JSON.stringify({ role: newRole }),
      });
    } catch (err: any) {
      setUsers(previous); // roll back on failure
      setError(err.message || "Failed to update role");
    }
  };

  const openResetPassword = (userId: string) => {
    setResettingUserId(userId);
    setNewPassword("");
    setResetStatus((prev) => ({ ...prev, [userId]: "" }));
  };

  const cancelResetPassword = () => {
    setResettingUserId(null);
    setNewPassword("");
  };

  const handleResetPassword = async (userId: string) => {
    if (!newPassword || newPassword.length < 6) {
      setResetStatus((prev) => ({
        ...prev,
        [userId]: "Password must be at least 6 characters",
      }));
      return;
    }

    try {
      await apiRequest(`${API_BASE_URL}/auth/admin/users/${userId}/reset-password`, {
        method: "PUT",
        body: JSON.stringify({ new_password: newPassword }),
      });
      setResetStatus((prev) => ({ ...prev, [userId]: "Password updated" }));
      setResettingUserId(null);
      setNewPassword("");
    } catch (err: any) {
      setResetStatus((prev) => ({
        ...prev,
        [userId]: err.message || "Failed to reset password",
      }));
    }
  };

  const handleCreateFormChange = (field: string, value: string) => {
    setCreateForm((prev) => ({ ...prev, [field]: value }));
    setCreateError("");
    setCreateSuccess("");
  };

  const handleCreateAccount = async () => {
    setCreateError("");
    setCreateSuccess("");

    if (!createForm.username || !createForm.email || !createForm.password) {
      setCreateError("Username, email, and password are required");
      return;
    }
    if (createForm.role === "player" && !createForm.player_id) {
      setCreateError("Select a player to link this account to");
      return;
    }

    setIsCreating(true);
    try {
      await apiRequest(`${API_BASE_URL}/auth/admin/users`, {
        method: "POST",
        body: JSON.stringify({
          username: createForm.username,
          email: createForm.email,
          password: createForm.password,
          role: createForm.role,
          player_id:
            createForm.role === "player" ? Number(createForm.player_id) : null,
        }),
      });

      setCreateSuccess("Account created successfully");
      setCreateForm({
        username: "",
        email: "",
        password: "",
        role: "coach",
        player_id: "",
      });
      fetchUsers();
    } catch (err: any) {
      setCreateError(err.message || "Failed to create account");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin</h1>
              <p className="text-gray-600">Manage users and roles</p>
            </div>
            <Button
              onClick={() => setShowCreateForm((v) => !v)}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              {showCreateForm ? "Close" : "Create Player/Coach Account"}
            </Button>
          </div>

          {showCreateForm && (
            <Card>
              <CardHeader>
                <CardTitle>Create Player or Coach Account</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {createError && (
                  <p className="text-sm text-red-600">{createError}</p>
                )}
                {createSuccess && (
                  <p className="text-sm text-green-600">{createSuccess}</p>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Username</Label>
                    <Input
                      value={createForm.username}
                      onChange={(e) =>
                        handleCreateFormChange("username", e.target.value)
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      value={createForm.email}
                      onChange={(e) =>
                        handleCreateFormChange("email", e.target.value)
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Temporary Password</Label>
                    <Input
                      type="password"
                      value={createForm.password}
                      onChange={(e) =>
                        handleCreateFormChange("password", e.target.value)
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Role</Label>
                    <Select
                      value={createForm.role}
                      onValueChange={(value) =>
                        handleCreateFormChange("role", value)
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="coach">Coach</SelectItem>
                        <SelectItem value="player">Player</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {createForm.role === "player" && (
                    <div className="space-y-2 md:col-span-2">
                      <Label>Link to Player</Label>
                      <Select
                        value={createForm.player_id}
                        onValueChange={(value) =>
                          handleCreateFormChange("player_id", value)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a player record" />
                        </SelectTrigger>
                        <SelectContent>
                          {availablePlayers.map((p) => (
                            <SelectItem key={p.id} value={p.id.toString()}>
                              #{p.jersey_number} {p.name} — {p.team}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>

                <Button
                  onClick={handleCreateAccount}
                  disabled={isCreating}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {isCreating ? "Creating..." : "Create Account"}
                </Button>
              </CardContent>
            </Card>
          )}

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
              {error}
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Users</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-sm text-gray-500">Loading users...</p>
              ) : users.length === 0 ? (
                <p className="text-sm text-gray-500">No users found.</p>
              ) : (
                <div className="space-y-2">
                  {users.map((u) => (
                    <div key={u.user_id} className="border-b py-3 last:border-b-0">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div>
                          <p className="font-medium text-gray-900">{u.username}</p>
                          <p className="text-sm text-gray-500">{u.email}</p>
                          {u.player_id && (
                            <p className="text-xs text-gray-400">
                              Linked player ID: {u.player_id}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Select
                            value={u.role}
                            onValueChange={(value) => handleRoleChange(u.user_id, value)}
                          >
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="user">User</SelectItem>
                              <SelectItem value="admin">Admin</SelectItem>
                              <SelectItem value="player">Player</SelectItem>
                              <SelectItem value="coach">Coach</SelectItem>
                            </SelectContent>
                          </Select>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              resettingUserId === u.user_id
                                ? cancelResetPassword()
                                : openResetPassword(u.user_id)
                            }
                          >
                            {resettingUserId === u.user_id ? "Cancel" : "Reset Password"}
                          </Button>
                        </div>
                      </div>

                      {resettingUserId === u.user_id && (
                        <div className="mt-3 flex items-center gap-2">
                          <Input
                            type="password"
                            placeholder="New password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className="w-64"
                          />
                          <Button
                            size="sm"
                            onClick={() => handleResetPassword(u.user_id)}
                          >
                            Save
                          </Button>
                        </div>
                      )}

                      {resetStatus[u.user_id] && (
                        <p
                          className={`mt-1 text-sm ${
                            resetStatus[u.user_id] === "Password updated"
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {resetStatus[u.user_id]}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}