import { useEffect } from "react";

export function useOAuthCallback(
  navigate: (path: string) => void,
  setError: (message: string) => void,
) {
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get("auth");
    const token = urlParams.get("token");
    const userParam = urlParams.get("user");
    const errorMessage = urlParams.get("message");

    if (authStatus === "success" && token && userParam) {
      try {
        const user = JSON.parse(decodeURIComponent(userParam));
        localStorage.setItem("isAuthenticated", "true");
        localStorage.setItem("userEmail", user.email);
        localStorage.setItem("userName", user.name);
        localStorage.setItem("authToken", token);
        localStorage.setItem("authProvider", user.provider);
        window.history.replaceState({}, document.title, window.location.pathname);
        navigate("/afl-dashboard");
      } catch (err) {
        console.error("Error parsing OAuth user data:", err);
        setError("Authentication failed. Please try again.");
      }
    } else if (authStatus === "error" && errorMessage) {
      setError(decodeURIComponent(errorMessage));
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [navigate, setError]);
}
