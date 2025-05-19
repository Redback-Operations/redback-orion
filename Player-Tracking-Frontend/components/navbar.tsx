"use client";

import Link from 'next/link';
import { MapPin } from 'lucide-react';
import { useSession, signOut } from 'next-auth/react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export default function Navbar() {
  const { data: session } = useSession();

  return (
    <nav className="fixed w-full z-50 bg-black/50 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <MapPin className="h-8 w-8 text-yellow-400" />
              <span className="ml-2 text-2xl font-bold text-yellow-400">Redback Operations</span>
            </Link>
          </div>

          <div className="hidden md:block">
            <div className="flex items-center space-x-8">
              <Link href="/user_image" className="text-white hover:text-yellow-400 transition-colors">
                VISION
              </Link>
              <Link href="/products" className="text-white hover:text-yellow-400 transition-colors">
                PRODUCTS
              </Link>
              <Link href="/models" className="text-white hover:text-yellow-400 transition-colors">
                MODELS
              </Link>
              <Link href="/player-dashboard" className="text-white hover:text-yellow-400 transition-colors">
                PLAYERS
              </Link>
              <Link href="/sports" className="text-white hover:text-yellow-400 transition-colors">
                SPORTS
              </Link>
              <Link href="/contact" className="text-white hover:text-yellow-400 transition-colors">
                CONTACT
              </Link>
              <Link href="/support" className="text-white hover:text-yellow-400 transition-colors">
                SUPPORT
              </Link>
              {session ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" className="border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black">
                      {session.user?.name || session.user?.email}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <DropdownMenuItem onClick={() => signOut()}>
                      Sign out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link href="/auth/signin">
                    <Button variant="outline" className="border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black">
                      Sign In
                    </Button>
                  </Link>
                  <Link href="/auth/signup">
                    <Button variant="outline" className="border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black">
                      Sign Up
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}