export default function PlayerTrackingPage() {
    return (
        <main className="min-h-screen bg-black text-white px-4 pt-32 pb-16 flex flex-col items-center text-center">
            <h1 className="text-4xl font-bold text-yellow-400 mb-4">Player Tracking Model</h1>
            <p className="text-gray-300 max-w-3xl mb-8">
                Our Player Tracking model tracks players' positions and movement across the field in real time,
                enabling coaches to analyze performance, positioning, and strategy.
                This page will soon allow video input to visualize AI-powered tracking overlays.
            </p>
            <div className="bg-white/10 border border-yellow-400 rounded-xl p-6 max-w-3xl w-full mb-8">
                <h2 className="text-2xl font-semibold text-yellow-300 mb-2">Coming Soon:</h2>
                <ul className="list-disc list-inside text-left text-gray-200">
                    <li>Upload gameplay footage</li>
                    <li>Visualize tracked positions</li>
                    <li>Download player movement data</li>
                </ul>
            </div>
            <p className="text-sm text-gray-500 mt-16">
                &copy; {new Date().getFullYear()} Redback Operations. All rights reserved.
            </p>
        </main>
    );
}
