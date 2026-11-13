import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Activity,
  Users,
  BarChart3,
  Video,
  Shield,
  Eye,
  EyeOff,
  Smartphone,
  Monitor,
  Mail,
  Lock,
  Building,
  ArrowLeft,
  CheckCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "@/lib/api";

export default function Login() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });

  const [signupForm, setSignupForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    organization: "",
    role: "",
    agreeTerms: false,
  });

  const [resetForm, setResetForm] = useState({
    email: "",
    resetCode: "",
    newPassword: "",
    confirmNewPassword: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);
  const [resetStep, setResetStep] = useState(1);
  const [resetMessage, setResetMessage] = useState("");

  const features = [
    {
      icon: Activity,
      title: "Player Performance",
      description: "Real-time player statistics and performance metrics",
    },
    {
      icon: Users,
      title: "Crowd Monitoring",
      description: "Stadium crowd density and safety analytics",
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Comprehensive reporting and data insights",
    },
    {
      icon: Video,
      title: "Video Analysis",
      description: "AI-powered match video analysis and highlights",
    },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      if (!loginForm.email || !loginForm.password) {
        setError("Please enter both email and password.");
        return;
      }

      const data = await apiRequest(
        "http://localhost:8000/login",
        {
          method: "POST",
          body: JSON.stringify({
            email: loginForm.email,
            password: loginForm.password,
          }),
        },
        false,
      );

      if (data?.access_token) {
        localStorage.setItem("authToken", data.access_token);
      }

      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("userEmail", loginForm.email);
      localStorage.setItem("userName", data?.user?.name || loginForm.email);

      setSuccess("Login successful.");
      console.log("Login successful");

      navigate("/player-performance");
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
      console.error("Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      if (
        !signupForm.firstName ||
        !signupForm.lastName ||
        !signupForm.email ||
        !signupForm.password ||
        !signupForm.organization
      ) {
        setError("Please fill all required fields.");
        return;
      }

      if (signupForm.password !== signupForm.confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      if (!signupForm.agreeTerms) {
        setError("Please agree to the terms of service.");
        return;
      }

      const data = await apiRequest(
        "http://localhost:8000/register",
        {
          method: "POST",
          body: JSON.stringify({
            first_name: signupForm.firstName,
            last_name: signupForm.lastName,
            email: signupForm.email,
            password: signupForm.password,
            organization: signupForm.organization,
            role: signupForm.role,
          }),
        },
        false,
      );

      if (data?.access_token) {
        localStorage.setItem("authToken", data.access_token);
      }

      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("userEmail", signupForm.email);
      localStorage.setItem(
        "userName",
        `${signupForm.firstName} ${signupForm.lastName}`,
      );

      setSuccess("Account created successfully.");
      console.log("Signup successful");

      navigate("/player-performance");
    } catch (err: any) {
      setError(err.message || "Unable to create account.");
      console.error("Signup failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleAuth = () => {
    window.location.href = "/api/auth/google";
  };

  const handleAppleAuth = () => {
    window.location.href = "/api/auth/apple";
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setResetMessage("");

    try {
      if (!resetForm.email) {
        setError("Please enter your email address.");
        return;
      }

      await apiRequest(
        "http://localhost:8000/forgot-password",
        {
          method: "POST",
          body: JSON.stringify({ email: resetForm.email }),
        },
        false,
      );

      setResetMessage(
        `Password reset instructions were sent to ${resetForm.email}.`,
      );
      setResetStep(2);
      console.log("Password reset email requested");
    } catch (err: any) {
      setError(err.message || "Unable to send reset instructions.");
      console.error("Forgot password failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyResetCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      if (!resetForm.resetCode) {
        setError("Please enter the verification code.");
        return;
      }

      await apiRequest(
        "http://localhost:8000/verify-reset-code",
        {
          method: "POST",
          body: JSON.stringify({
            email: resetForm.email,
            reset_code: resetForm.resetCode,
          }),
        },
        false,
      );

      setResetStep(3);
      console.log("Reset code verified");
    } catch (err: any) {
      setError(err.message || "Invalid verification code.");
      console.error("Reset code verification failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      if (!resetForm.newPassword || !resetForm.confirmNewPassword) {
        setError("Please enter and confirm your new password.");
        return;
      }

      if (resetForm.newPassword !== resetForm.confirmNewPassword) {
        setError("Passwords do not match.");
        return;
      }

      await apiRequest(
        "http://localhost:8000/reset-password",
        {
          method: "POST",
          body: JSON.stringify({
            email: resetForm.email,
            reset_code: resetForm.resetCode,
            new_password: resetForm.newPassword,
          }),
        },
        false,
      );

      setResetStep(4);
      console.log("Password reset successful");
    } catch (err: any) {
      setError(err.message || "Unable to reset password.");
      console.error("Password reset failed");
    } finally {
      setIsLoading(false);
    }
  };

  const closeResetModal = () => {
    setIsResetModalOpen(false);
    setResetStep(1);
    setResetForm({
      email: "",
      resetCode: "",
      newPassword: "",
      confirmNewPassword: "",
    });
    setError("");
    setResetMessage("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  AFL Analytics
                </h1>
                <p className="text-sm text-gray-600">
                  Professional Sports Analytics Platform
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="hidden sm:flex">
                <Monitor className="w-3 h-3 mr-1" />
                Web App
              </Badge>
              <Badge variant="outline">
                <Smartphone className="w-3 h-3 mr-1" />
                Mobile Optimized
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div className="space-y-6">
              <div className="space-y-4">
                <Badge variant="secondary" className="w-fit">
                  <Shield className="w-3 h-3 mr-1" />
                  Trusted by AFL Teams
                </Badge>
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
                  Professional AFL
                  <span className="block bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                    Analytics Platform
                  </span>
                </h2>
                <p className="text-lg text-gray-600">
                  Comprehensive player performance tracking, crowd monitoring,
                  and match analytics designed specifically for Australian
                  Football League professionals.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {features.map((feature, index) => {
                  const Icon = feature.icon;
                  return (
                    <div
                      key={index}
                      className="p-4 bg-white rounded-lg border shadow-sm"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-green-100 to-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Icon className="w-4 h-4 text-green-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {feature.title}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="w-full max-w-md mx-auto">
              <Card className="shadow-lg">
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">Welcome Back</CardTitle>
                  <CardDescription>
                    Sign in to access your AFL analytics dashboard
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <Tabs defaultValue="login" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="login">Sign In</TabsTrigger>
                      <TabsTrigger value="signup">Sign Up</TabsTrigger>
                    </TabsList>

                    <TabsContent value="login" className="space-y-4">
                      {error && (
                        <Alert variant="destructive">
                          <AlertDescription>{error}</AlertDescription>
                        </Alert>
                      )}

                      {success && (
                        <Alert>
                          <AlertDescription>{success}</AlertDescription>
                        </Alert>
                      )}

                      <div className="space-y-3">
                        <Button
                          type="button"
                          variant="outline"
                          className="w-full"
                          onClick={handleGoogleAuth}
                        >
                          Continue with Google
                        </Button>

                        <Button
                          type="button"
                          variant="outline"
                          className="w-full bg-black text-white hover:bg-gray-800"
                          onClick={handleAppleAuth}
                        >
                          Continue with Apple
                        </Button>

                        <div className="relative">
                          <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t" />
                          </div>
                          <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-background px-2 text-muted-foreground">
                              Or continue with email
                            </span>
                          </div>
                        </div>
                      </div>

                      <form onSubmit={handleLogin} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="email">Email Address</Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="email"
                              type="email"
                              placeholder="your@email.com"
                              value={loginForm.email}
                              onChange={(e) =>
                                setLoginForm({
                                  ...loginForm,
                                  email: e.target.value,
                                })
                              }
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="password">Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="password"
                              type={showPassword ? "text" : "password"}
                              placeholder="Enter your password"
                              value={loginForm.password}
                              onChange={(e) =>
                                setLoginForm({
                                  ...loginForm,
                                  password: e.target.value,
                                })
                              }
                              className="pl-10 pr-10"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="remember"
                              checked={loginForm.rememberMe}
                              onCheckedChange={(checked) =>
                                setLoginForm({
                                  ...loginForm,
                                  rememberMe: checked as boolean,
                                })
                              }
                            />
                            <Label htmlFor="remember" className="text-sm">
                              Remember me
                            </Label>
                          </div>

                          <button
                            type="button"
                            onClick={() => setIsResetModalOpen(true)}
                            className="text-sm text-blue-600 hover:underline"
                          >
                            Forgot password?
                          </button>
                        </div>

                        <Button
                          type="submit"
                          className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                          disabled={isLoading}
                        >
                          {isLoading ? "Signing In..." : "Sign In"}
                        </Button>
                      </form>
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-4">
                      {error && (
                        <Alert variant="destructive">
                          <AlertDescription>{error}</AlertDescription>
                        </Alert>
                      )}

                      {success && (
                        <Alert>
                          <AlertDescription>{success}</AlertDescription>
                        </Alert>
                      )}

                      <form onSubmit={handleSignup} className="space-y-4">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-2">
                            <Label htmlFor="firstName">First Name</Label>
                            <Input
                              id="firstName"
                              placeholder="John"
                              value={signupForm.firstName}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  firstName: e.target.value,
                                })
                              }
                              required
                            />
                          </div>

                          <div className="space-y-2">
                            <Label htmlFor="lastName">Last Name</Label>
                            <Input
                              id="lastName"
                              placeholder="Doe"
                              value={signupForm.lastName}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  lastName: e.target.value,
                                })
                              }
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="signupEmail">Email Address</Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="signupEmail"
                              type="email"
                              placeholder="your@email.com"
                              value={signupForm.email}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  email: e.target.value,
                                })
                              }
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="organization">Organization</Label>
                          <div className="relative">
                            <Building className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="organization"
                              placeholder="AFL Team or Organization"
                              value={signupForm.organization}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  organization: e.target.value,
                                })
                              }
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="signupPassword">Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="signupPassword"
                              type="password"
                              placeholder="Create a strong password"
                              value={signupForm.password}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  password: e.target.value,
                                })
                              }
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="confirmPassword">
                            Confirm Password
                          </Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                              id="confirmPassword"
                              type="password"
                              placeholder="Confirm your password"
                              value={signupForm.confirmPassword}
                              onChange={(e) =>
                                setSignupForm({
                                  ...signupForm,
                                  confirmPassword: e.target.value,
                                })
                              }
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="terms"
                            checked={signupForm.agreeTerms}
                            onCheckedChange={(checked) =>
                              setSignupForm({
                                ...signupForm,
                                agreeTerms: checked as boolean,
                              })
                            }
                            required
                          />
                          <Label htmlFor="terms" className="text-sm">
                            I agree to the Terms of Service and Privacy Policy
                          </Label>
                        </div>

                        <Button
                          type="submit"
                          className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                          disabled={isLoading}
                        >
                          {isLoading ? "Creating Account..." : "Create Account"}
                        </Button>
                      </form>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      <Dialog open={isResetModalOpen} onOpenChange={setIsResetModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {resetStep > 1 && resetStep < 4 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setResetStep(Math.max(1, resetStep - 1))}
                  className="p-0 h-6 w-6"
                >
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              )}
              {resetStep === 1 && "Reset Password"}
              {resetStep === 2 && "Enter Verification Code"}
              {resetStep === 3 && "Create New Password"}
              {resetStep === 4 && "Password Reset Complete"}
            </DialogTitle>
            <DialogDescription>
              {resetStep === 1 &&
                "Enter your email to receive reset instructions"}
              {resetStep === 2 && "Check your email for a verification code"}
              {resetStep === 3 && "Enter your new password"}
              {resetStep === 4 && "Your password has been successfully reset"}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {resetMessage && resetStep === 2 && (
              <Alert>
                <AlertDescription>{resetMessage}</AlertDescription>
              </Alert>
            )}

            {resetStep === 1 && (
              <form onSubmit={handleForgotPassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="resetEmail">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="resetEmail"
                      type="email"
                      placeholder="your@email.com"
                      value={resetForm.email}
                      onChange={(e) =>
                        setResetForm({ ...resetForm, email: e.target.value })
                      }
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Sending..." : "Send Reset Link"}
                </Button>
              </form>
            )}

            {resetStep === 2 && (
              <form onSubmit={handleVerifyResetCode} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="resetCode">Verification Code</Label>
                  <Input
                    id="resetCode"
                    type="text"
                    placeholder="Enter code"
                    value={resetForm.resetCode}
                    onChange={(e) =>
                      setResetForm({ ...resetForm, resetCode: e.target.value })
                    }
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Verifying..." : "Verify Code"}
                </Button>
              </form>
            )}

            {resetStep === 3 && (
              <form onSubmit={handleResetPassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="Enter new password"
                    value={resetForm.newPassword}
                    onChange={(e) =>
                      setResetForm({
                        ...resetForm,
                        newPassword: e.target.value,
                      })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmNewPassword">
                    Confirm New Password
                  </Label>
                  <Input
                    id="confirmNewPassword"
                    type="password"
                    placeholder="Confirm new password"
                    value={resetForm.confirmNewPassword}
                    onChange={(e) =>
                      setResetForm({
                        ...resetForm,
                        confirmNewPassword: e.target.value,
                      })
                    }
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Resetting..." : "Reset Password"}
                </Button>
              </form>
            )}

            {resetStep === 4 && (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <h3 className="font-medium text-green-900">Success!</h3>
                  <p className="text-sm text-green-700">
                    Your password has been reset successfully.
                  </p>
                </div>
                <Button onClick={closeResetModal} className="w-full">
                  Continue to Sign In
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
