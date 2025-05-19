import { useRouter } from "next/router";
import Image from "next/image";

export default function PlayerProfile() {
  const router = useRouter();
  const {
    name,
    photo,
    position,
    team,
    age,
    nationality,
    bio,
    goals,
    assists,
    distance,
    speed,
    passes,
    tackles,
    minutes,
  } = router.query;

  if (!name) return <p className="text-center mt-10">Loading player details...</p>;

  return (
    <div className="min-h-screen bg-background text-foreground px-6 py-12">
      <div className="text-center max-w-2xl mx-auto">
        <Image
          src={photo as string}
          alt={name as string}
          width={160}
          height={160}
          className="mx-auto rounded-full object-cover"
        />
        <h1 className="text-3xl font-bold mt-4">{name}</h1>
        <p className="text-muted-foreground text-sm mb-2">{position} — {team}</p>
        <p className="text-sm">Age: {age} | Nationality: {nationality}</p>
        <p className="mt-4 italic text-gray-400">{bio}</p>

        <div className="mt-6 text-left bg-card p-6 rounded-lg shadow border border-border">
          <h2 className="text-xl font-semibold text-primary mb-4">Performance Stats</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            {goals && <li>🎯 <strong className="text-white">Goals:</strong> {goals}</li>}
            {assists && <li>🅰️ <strong className="text-white">Assists:</strong> {assists}</li>}
            {distance && <li>🏃 <strong className="text-white">Distance Covered:</strong> {distance} km</li>}
            {speed && <li>⚡ <strong className="text-white">Top Speed:</strong> {speed} km/h</li>}
            {passes && <li>🎯 <strong className="text-white">Passes Completed:</strong> {passes}</li>}
            {tackles && <li>🛡 <strong className="text-white">Tackles Won:</strong> {tackles}</li>}
            {minutes && <li>⏱ <strong className="text-white">Minutes Played:</strong> {minutes}</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
