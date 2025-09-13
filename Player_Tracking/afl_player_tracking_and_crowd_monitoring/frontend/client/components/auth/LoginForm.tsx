import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";

export type LoginValues = {
  email: string;
  password: string;
  rememberMe: boolean;
};

export default function LoginForm({
  values,
  showPassword,
  onToggleShowPassword,
  onChange,
  onSubmit,
  isLoading,
  onForgotPassword,
}: {
  values: LoginValues;
  showPassword: boolean;
  onToggleShowPassword: () => void;
  onChange: (update: Partial<LoginValues>) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  onForgotPassword: () => void;
}) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email Address</Label>
        <div className="relative">
          <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            id="email"
            type="email"
            placeholder="your@email.com"
            value={values.email}
            onChange={(e) => onChange({ email: e.target.value })}
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
            value={values.password}
            onChange={(e) => onChange({ password: e.target.value })}
            className="pl-10 pr-10"
            required
          />
          <button
            type="button"
            onClick={onToggleShowPassword}
            className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="remember"
            checked={values.rememberMe}
            onCheckedChange={(checked) => onChange({ rememberMe: checked as boolean })}
          />
          <Label htmlFor="remember" className="text-sm">Remember me</Label>
        </div>
        <button type="button" onClick={onForgotPassword} className="text-sm text-orange-600 hover:underline">
          Forgot password?
        </button>
      </div>

      <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-orange-600" disabled={isLoading}>
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
  );
}
