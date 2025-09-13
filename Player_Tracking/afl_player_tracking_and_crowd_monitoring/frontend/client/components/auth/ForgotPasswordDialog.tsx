import React, { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Mail, Lock, ArrowLeft, CheckCircle } from "lucide-react";
import { sendResetEmail, verifyResetCode, resetPassword, RESET_DEMO_CODE } from "@/lib/auth";

export default function ForgotPasswordDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({ email: "", code: "", newPassword: "", confirmNewPassword: "" });

  const close = () => {
    onOpenChange(false);
    setStep(1);
    setForm({ email: "", code: "", newPassword: "", confirmNewPassword: "" });
    setError("");
    setMessage("");
  };

  const onSendEmail: React.FormEventHandler = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    const res = await sendResetEmail(form.email);
    if (res.success) {
      setMessage(`Reset link sent to ${form.email}`);
      setStep(2);
    } else {
      if ("message" in res) setError(res.message);
    }
    setIsLoading(false);
  };

  const onVerify: React.FormEventHandler = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    const res = await verifyResetCode(form.code);
    if (res.success) {
      setStep(3);
    } else {
      if ("message" in res) setError(res.message);
    }
    setIsLoading(false);
  };

  const onReset: React.FormEventHandler = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    const res = await resetPassword(form.newPassword, form.confirmNewPassword);
    if (res.success) {
      setStep(4);
    } else {
      if ("message" in res) setError(res.message);
    }
    setIsLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {step > 1 && step < 4 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setStep(step === 2 ? 1 : 2)}
                className="p-0 h-6 w-6"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            {step === 1 && "Reset Password"}
            {step === 2 && "Enter Verification Code"}
            {step === 3 && "Create New Password"}
            {step === 4 && "Password Reset Complete"}
          </DialogTitle>
          <DialogDescription>
            {step === 1 && "Enter your email to receive a reset link"}
            {step === 2 && "Check your email for a verification code"}
            {step === 3 && "Enter your new password"}
            {step === 4 && "Your password has been successfully reset"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {message && step === 2 && (
            <Alert>
              <Mail className="h-4 w-4" />
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          {step === 1 && (
            <form onSubmit={onSendEmail} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resetEmail">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="resetEmail"
                    type="email"
                    placeholder="your@email.com"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-orange-600" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Sending Reset Link...
                  </div>
                ) : (
                  "Send Reset Link"
                )}
              </Button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={onVerify} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resetCode">Verification Code</Label>
                <Input
                  id="resetCode"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                  maxLength={6}
                  required
                />
                <p className="text-xs text-gray-600">
                  For demo purposes, use code: <strong>{RESET_DEMO_CODE}</strong>
                </p>
              </div>
              <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-orange-600" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Verifying...
                  </div>
                ) : (
                  "Verify Code"
                )}
              </Button>
            </form>
          )}

          {step === 3 && (
            <form onSubmit={onReset} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="Enter new password"
                    value={form.newPassword}
                    onChange={(e) => setForm({ ...form, newPassword: e.target.value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmNewPassword">Confirm New Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmNewPassword"
                    type="password"
                    placeholder="Confirm new password"
                    value={form.confirmNewPassword}
                    onChange={(e) => setForm({ ...form, confirmNewPassword: e.target.value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-orange-600" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Resetting Password...
                  </div>
                ) : (
                  "Reset Password"
                )}
              </Button>
            </form>
          )}

          {step === 4 && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-green-900">Success!</h3>
                <p className="text-sm text-green-700">Your password has been reset successfully.</p>
              </div>
              <Button onClick={close} className="w-full bg-gradient-to-r from-purple-600 to-orange-600">
                Continue to Sign In
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
