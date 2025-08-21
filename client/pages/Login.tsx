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
  Activity,
  Users,
  BarChart3,
  Video,
  Shield,
  Eye,
  EyeOff,
  Smartphone,
  Monitor,
  User,
  Mail,
  Lock,
  Building,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

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
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Simulate login process
    await new Promise((resolve) => setTimeout(resolve, 1500));

    if (loginForm.email && loginForm.password) {
      // Successful login - redirect to dashboard
      navigate("/afl-dashboard");
    } else {
      setError("Please enter valid credentials");
    }

    setIsLoading(false);
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    if (signupForm.password !== signupForm.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    // Simulate signup process
    await new Promise((resolve) => setTimeout(resolve, 2000));

    if (signupForm.email && signupForm.password && signupForm.agreeTerms) {
      // Successful signup - redirect to dashboard
      navigate("/afl-dashboard");
    } else {
      setError("Please fill all required fields and agree to terms");
    }

    setIsLoading(false);
  };

  const demoLogin = () => {
    setLoginForm({
      email: "demo@aflanalytics.com",
      password: "demo123",
      rememberMe: true,
    });
  };

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
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
            {/* Left side - Features & Info */}
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

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <User className="w-4 h-4 text-blue-600" />
                  <span className="font-medium text-blue-900">Demo Access</span>
                </div>
                <p className="text-sm text-blue-700 mb-3">
                  Try the platform with demo credentials to explore all features
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={demoLogin}
                  className="text-blue-600 border-blue-300 hover:bg-blue-100"
                >
                  Load Demo Credentials
                </Button>
              </div>
            </div>

            {/* Right side - Login/Signup Form */}
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
                          {isLoading ? (
                            <div className="flex items-center">
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                              Signing In...
                            </div>
                          ) : (
                            "Sign In"
                          )}
                        </Button>
                      </form>
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-4">
                      {error && (
                        <Alert variant="destructive">
                          <AlertDescription>{error}</AlertDescription>
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
                            I agree to the{" "}
                            <button
                              type="button"
                              className="text-blue-600 hover:underline"
                            >
                              Terms of Service
                            </button>{" "}
                            and{" "}
                            <button
                              type="button"
                              className="text-blue-600 hover:underline"
                            >
                              Privacy Policy
                            </button>
                          </Label>
                        </div>

                        <Button
                          type="submit"
                          className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                          disabled={isLoading}
                        >
                          {isLoading ? (
                            <div className="flex items-center">
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                              Creating Account...
                            </div>
                          ) : (
                            "Create Account"
                          )}
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
    </div>
  );
}
