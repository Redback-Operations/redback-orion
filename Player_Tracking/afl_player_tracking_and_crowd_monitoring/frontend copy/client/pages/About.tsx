import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MobileNavigation from "@/components/MobileNavigation";

export default function About() {
  return (
    <div>
      <MobileNavigation />

      <div>
        <h1>About the project</h1>
        <p> Project 4, RedBack Orion is one of our company's project that aims to redefine sports engagment.
          This project's main goal is to create an intelligent, real time tracking system for athletes in multiple fields of sports, 
          especially one of Austrlia's biggest sports: Footy. Where not we track every single player in every single team, keep track of their individual 
          stats live, but we also track the density of the crowd in the stadium, to maintain safety of the audience during peak time
        </p>

        <h1>Features</h1>
        <h2> Player Performance</h2>
        <h2>Crowd Monitoring</h2>
        <h2>Analytics</h2>
        <h2>Reports</h2>
        <h2>API Diagnostics</h2>
      </div>
    </div>
  );
}