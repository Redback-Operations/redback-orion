import { withAuth } from "next-auth/middleware"

export default withAuth({
  callbacks: {
    authorized({ req, token }) {
      // Return true if the user is authenticated
      return !!token
    },
  },
})

// Protect these routes - add any routes that require authentication
export const config = { 
  matcher: [
    "/products/:path*",
    "/sports/:path*",
  ]
}