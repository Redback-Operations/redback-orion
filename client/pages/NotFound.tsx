import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Home, ArrowLeft, Search, AlertTriangle } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();

  const popularPages = [
    { name: "Dashboard", href: "/afl-dashboard", icon: Activity },
    { name: "Player Performance", href: "/player-performance", icon: Activity },
    { name: "Crowd Monitor", href: "/crowd-monitor", icon: Activity },
    { name: "Analytics", href: "/analytics", icon: Activity },
    { name: "Reports", href: "/reports", icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex flex-col">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/afl-dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              AFL Analytics
            </span>
          </Link>
          <Badge variant="outline" className="text-orange-600 border-orange-200">
            404 Error
          </Badge>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="max-w-2xl w-full">
          <Card className="text-center border-0 shadow-lg mb-6">
            <CardHeader className="pb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-100 to-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-10 h-10 text-orange-600" />
              </div>
              <CardTitle className="text-3xl">Page Not Found</CardTitle>
              <CardDescription className="text-lg">
                The page you're looking for doesn't exist or has been moved.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-gray-600">
                Don't worry! This happens sometimes. You can go back to the previous page
                or navigate to one of our main sections below.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  asChild
                  className="bg-gradient-to-r from-green-600 to-blue-600 flex-1"
                >
                  <Link to="/afl-dashboard">
                    <Home className="w-4 h-4 mr-2" />
                    Go to Dashboard
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate(-1)}
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Go Back
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Popular Pages */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="w-5 h-5" />
                Popular Pages
              </CardTitle>
              <CardDescription>
                Quick access to commonly used sections
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {popularPages.map((page) => {
                  const Icon = page.icon;
                  return (
                    <Link
                      key={page.name}
                      to={page.href}
                      className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-8 h-8 bg-gradient-to-br from-green-100 to-blue-100 rounded-lg flex items-center justify-center">
                        <Icon className="w-4 h-4 text-green-600" />
                      </div>
                      <span className="font-medium text-gray-700">{page.name}</span>
                    </Link>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
