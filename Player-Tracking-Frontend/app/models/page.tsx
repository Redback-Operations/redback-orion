"use client";
import ObjectDetectionCard from "@/components/models/ObjectDetectionCard";
import PlayerTrackingCard from "@/components/models/PlayerTrackingCard";

export default function ModelsPage() {
    return (
        <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-4 py-16">
            <div className="w-full max-w-7xl text-center">
                <h1 className="text-5xl font-bold text-yellow-400 mb-4">Redback Models</h1>
                <h2 className="text-lg text-gray-400 mb-12">
                    Explore our state-of-the-art AI solutions built for real-time sports performance analysis.
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-items-center">
                    <ObjectDetectionCard />
                    <PlayerTrackingCard />
                    <div className="bg-gray-800 p-6 rounded-xl border border-yellow-400 text-center opacity-50 max-w-sm w-full">
                        <h2 className="text-xl font-bold text-yellow-400 mb-2">Coming Soon</h2>
                        <p className="text-sm text-gray-300">Stay tuned for our next AI-powered innovation.</p>
                    </div>
                </div>

                <div className="mt-12">
                    <button className="bg-yellow-400 text-black px-6 py-2 rounded-lg hover:bg-yellow-500 transition">
                        Request a Demo
                    </button>
                </div>

                <footer className="text-center text-gray-500 text-sm mt-16">
                    &copy; {new Date().getFullYear()} Redback Operations. All rights reserved.
                </footer>
            </div>
        </main>
    );
}
