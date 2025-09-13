import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Mail, Lock, Building } from "lucide-react";

export type SignupValues = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  organization: string;
  role: string;
  agreeTerms: boolean;
};

export default function SignupForm({
  values,
  onChange,
  onSubmit,
  isLoading,
}: {
  values: SignupValues;
  onChange: (update: Partial<SignupValues>) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="firstName">First Name</Label>
          <Input
            id="firstName"
            placeholder="John"
            value={values.firstName}
            onChange={(e) => onChange({ firstName: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName">Last Name</Label>
          <Input
            id="lastName"
            placeholder="Doe"
            value={values.lastName}
            onChange={(e) => onChange({ lastName: e.target.value })}
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
            value={values.email}
            onChange={(e) => onChange({ email: e.target.value })}
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
            value={values.organization}
            onChange={(e) => onChange({ organization: e.target.value })}
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
            value={values.password}
            onChange={(e) => onChange({ password: e.target.value })}
            className="pl-10"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm Password</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            id="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            value={values.confirmPassword}
            onChange={(e) => onChange({ confirmPassword: e.target.value })}
            className="pl-10"
            required
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="terms"
          checked={values.agreeTerms}
          onCheckedChange={(checked) => onChange({ agreeTerms: checked as boolean })}
          required
        />
        <Label htmlFor="terms" className="text-sm">
          I agree to the {" "}
          <button type="button" className="text-orange-600 hover:underline">Terms of Service</button> and {" "}
          <button type="button" className="text-orange-600 hover:underline">Privacy Policy</button>
        </Label>
      </div>

      <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-orange-600" disabled={isLoading}>
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
  );
}
