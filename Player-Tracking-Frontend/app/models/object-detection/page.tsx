export default function ObjectDetectionPage() {
    return (
        <main className="min-h-screen bg-black text-white px-4 pt-32 pb-16 flex flex-col items-center text-center">
            <h1 className="text-4xl font-bold text-yellow-400 mb-4">Object Detection Model</h1>
            <p className="text-gray-300 max-w-3xl mb-8">
                Our Object Detection model uses advanced deep learning to identify and classify objects in real-time video feeds.
                It provides tactical insights for sports analysis, surveillance, and smart automation. Below you'll find visualizations,
                technical specs, and sample outputs.
            </p>
            <div className="bg-white/10 border border-yellow-400 rounded-xl p-6 max-w-3xl w-full mb-8">
                <h2 className="text-2xl font-semibold text-yellow-300 mb-2">Coming Soon:</h2>
                <ul className="list-disc list-inside text-left text-gray-200">
                    <li>Upload image for object detection</li>
                    <li>View real-time predictions</li>
                    <li>Download annotated outputs</li>
                </ul>
            </div>
            <p className="text-sm text-gray-500 mt-16">
                &copy; {new Date().getFullYear()} Redback Operations. All rights reserved.
            </p>
        </main>
    );
}
