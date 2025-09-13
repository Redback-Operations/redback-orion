import { useState } from "react";
import HeaderBrand from "@/components/auth/HeaderBrand";
import AuthProviderButtons from "@/components/auth/AuthProviderButtons";
import AuthHero from "@/components/auth/AuthHero";
import LoginForm from "@/components/auth/LoginForm";
import SignupForm from "@/components/auth/SignupForm";
import ForgotPasswordDialog from "@/components/auth/ForgotPasswordDialog";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useNavigate } from "react-router-dom";
import { loginWithEmail, signupWithEmail } from "@/lib/auth";
import { useOAuthCallback } from "@/hooks/use-oauth";

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
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    const res = await loginWithEmail({ email: loginForm.email, password: loginForm.password });
    if (res.success) {
      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("userEmail", loginForm.email);
      navigate("/afl-dashboard");
    } else {
      if ("message" in res) setError(res.message);
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
    if (!signupForm.agreeTerms) {
      setError("Please agree to the terms of service");
      setIsLoading(false);
      return;
    }

    const res = await signupWithEmail({
      firstName: signupForm.firstName,
      lastName: signupForm.lastName,
      email: signupForm.email,
      password: signupForm.password,
      organization: signupForm.organization,
      role: signupForm.role,
    });
    if (res.success) {
      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("userEmail", signupForm.email);
      localStorage.setItem("userName", `${signupForm.firstName} ${signupForm.lastName}`);
      setSignupForm({
        firstName: "",
        lastName: "",
        email: "",
        password: "",
        confirmPassword: "",
        organization: "",
        role: "",
        agreeTerms: false,
      });
      navigate("/afl-dashboard");
    } else {
      if ("message" in res) setError(res.message);
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

  // OAuth authentication handlers
  const handleGoogleAuth = () => {
    window.location.href = "/api/auth/google";
  };

  const handleAppleAuth = () => {
    window.location.href = "/api/auth/apple";
  };

  useOAuthCallback(navigate, setError);






  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50">
      {/* Header */}
      <HeaderBrand />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <AuthHero onLoadDemo={demoLogin} />

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

                      {/* OAuth Buttons */}
                      <AuthProviderButtons mode="login" onGoogle={handleGoogleAuth} onApple={handleAppleAuth} />

                      <LoginForm
                        values={loginForm}
                        showPassword={showPassword}
                        onToggleShowPassword={() => setShowPassword(!showPassword)}
                        onChange={(u) => setLoginForm({ ...loginForm, ...u })}
                        onSubmit={handleLogin}
                        isLoading={isLoading}
                        onForgotPassword={() => setIsResetModalOpen(true)}
                      />
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-4">
                      {error && (
                        <Alert variant="destructive">
                          <AlertDescription>{error}</AlertDescription>
                        </Alert>
                      )}

                      {/* OAuth Buttons */}
                      <AuthProviderButtons mode="signup" onGoogle={handleGoogleAuth} onApple={handleAppleAuth} />

                      <SignupForm
                        values={signupForm}
                        onChange={(u) => setSignupForm({ ...signupForm, ...u })}
                        onSubmit={handleSignup}
                        isLoading={isLoading}
                      />
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      <ForgotPasswordDialog open={isResetModalOpen} onOpenChange={setIsResetModalOpen} />
    </div>
  );
}
