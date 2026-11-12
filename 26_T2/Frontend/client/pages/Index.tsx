import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Sparkles,
  Wand2,
  Code,
  Download,
  ArrowRight,
  Play,
  Image,
  Type,
  Smartphone,
  Monitor,
  Palette,
} from "lucide-react";

export default function Index() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    // Simulate generation time
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setIsGenerating(false);
  };

  const examples = [
    {
      title: "Meditation App",
      description:
        "Create a calming journaling app with soft, pastel colors (light blues and lavenders), a full-width header featuring the app logo and title, a large central text box with rounded corners and subtle shadow for writing entries",
      category: "Mobile App",
    },
    {
      title: "E-commerce Homepage",
      description:
        "A clean and warm-looking e-commerce homepage for a clothing startup called Skatee. Includes hero section, featured products, and a newsletter banner",
      category: "Website",
    },
    {
      title: "Task Management",
      description:
        "Create a mobile application that allows users to manage and display a to-do list of tasks with checkboxes and an add button",
      category: "Productivity",
    },
  ];

  const features = [
    {
      icon: Type,
      title: "Text to UI",
      description:
        "Transform natural language descriptions into beautiful UI designs",
    },
    {
      icon: Image,
      title: "Image to Design",
      description:
        "Upload sketches or wireframes to generate polished interfaces",
    },
    {
      icon: Smartphone,
      title: "Responsive Design",
      description:
        "Every design adapts perfectly to mobile, tablet, and desktop",
    },
    {
      icon: Code,
      title: "Export Code",
      description: "Get production-ready HTML, CSS, and React components",
    },
    {
      icon: Palette,
      title: "Custom Branding",
      description: "Apply your brand colors, fonts, and design system",
    },
    {
      icon: Monitor,
      title: "Live Preview",
      description: "See your designs come to life in real-time",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Wand2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Stitch
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <a
              href="#"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Features
            </a>
            <a
              href="#"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Examples
            </a>
            <a
              href="/afl-dashboard"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              AFL Dashboard
            </a>
            <a
              href="#"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Docs
            </a>
            <Button variant="outline" size="sm">
              Sign In
            </Button>
            <Button
              size="sm"
              className="bg-gradient-to-r from-blue-600 to-purple-600"
            >
              Get Started
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <Badge
          variant="secondary"
          className="mb-4 bg-blue-100 text-blue-700 border-blue-200"
        >
          <Sparkles className="w-3 h-3 mr-1" />
          AI-Powered UI Design
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Design UIs with
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {" "}
            Natural Language
          </span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your ideas into beautiful, functional user interfaces
          instantly. Just describe what you want, and our AI will create
          pixel-perfect designs with production-ready code.
        </p>

        {/* Prompt Input */}
        <div className="max-w-4xl mx-auto mb-12">
          <Card className="border-2 border-gray-200 shadow-lg">
            <CardContent className="p-6">
              <Textarea
                placeholder="Describe your UI design... e.g., 'Create a modern dashboard for a fitness app with dark theme, metrics cards, and a workout calendar'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[120px] text-lg border-0 focus-visible:ring-0 resize-none"
              />
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <span>Try:</span>
                  <button
                    className="text-blue-600 hover:underline"
                    onClick={() =>
                      setPrompt(
                        "Create a meditation app with calming blue colors and minimalist design",
                      )
                    }
                  >
                    Meditation app
                  </button>
                  <span>•</span>
                  <button
                    className="text-blue-600 hover:underline"
                    onClick={() =>
                      setPrompt(
                        "Design an e-commerce product page with modern layout and clean typography",
                      )
                    }
                  >
                    E-commerce page
                  </button>
                </div>
                <Button
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || isGenerating}
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Generate Design
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap justify-center gap-4 mb-16">
          <Button variant="outline" size="lg" className="group">
            <Image className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
            Upload Sketch
          </Button>
          <Button variant="outline" size="lg" className="group">
            <Code className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
            View Examples
          </Button>
          <Button variant="outline" size="lg" className="group">
            <Download className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
            Export Options
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Everything you need to design faster
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            From concept to code in minutes. Our AI understands design patterns,
            accessibility, and modern web standards.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={index}
                className="border-0 shadow-md hover:shadow-lg transition-shadow duration-300"
              >
                <CardHeader>
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Examples Section */}
      <section className="container mx-auto px-4 py-16 bg-gray-50 rounded-3xl mx-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Inspiration from the community
          </h2>
          <p className="text-xl text-gray-600">
            See what others are building with Stitch
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {examples.map((example, index) => (
            <Card
              key={index}
              className="hover:shadow-lg transition-shadow duration-300 cursor-pointer group"
            >
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                    {example.title}
                  </CardTitle>
                  <Badge variant="secondary" className="text-xs">
                    {example.category}
                  </Badge>
                </div>
                <CardDescription className="text-sm line-clamp-3">
                  {example.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-blue-600 text-sm font-medium group-hover:gap-2 transition-all">
                  Try this prompt
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Ready to revolutionize your design workflow?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of designers and developers who are building faster
            with AI
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-lg px-8"
            >
              Start Creating Free
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-6 h-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-md flex items-center justify-center">
                <Wand2 className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-gray-900">Stitch</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-gray-900 transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-gray-900 transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-gray-900 transition-colors">
                Support
              </a>
              <Separator orientation="vertical" className="h-4" />
              <span>© 2024 Stitch. All rights reserved.</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
