"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ImageVisionUploader() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState("");
  const [processedImageUrl, setProcessedImageUrl] = useState("");
  const [resultJson, setResultJson] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setProcessedImageUrl("");
      setResultJson(null);
    }
  };

  const handleSubmit = async () => {
    if (!imageFile) return alert("Please upload an image.");

    const formData = new FormData();
    formData.append("file", imageFile);

    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const dagId = process.env.NEXT_PUBLIC_DAG_ID;

    try {
      setLoading(true);

      const uploadRes = await fetch(`${apiUrl}/upload/?dag_id=${dagId}`, {
        method: "POST",
        body: formData,
      });

      const uploadJson = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploadJson.detail || "Upload failed.");

      // Result is stringified JSON inside `uploadJson.result`
      const parsedResult =
        typeof uploadJson.result === "string"
          ? JSON.parse(uploadJson.result)
          : uploadJson.result;

      setResultJson(parsedResult);
      setProcessedImageUrl(""); // Replace with actual URL if returned
      setLoading(false);
      alert("Image uploaded and metadata received.");
    } catch (err) {
      console.error("Upload error:", err);
      alert("Failed to upload image.");
      setLoading(false);
    }
  };

  return (
    <div className="pt-20 grid gap-6 max-w-6xl mx-auto">
      <p className="text-sm text-muted-foreground">
        Upload an image to generate AI vision results through Kafka.
      </p>

      {/* Upload Form */}
      <Card className="grid md:grid-cols-2 gap-4">
        <CardContent className="p-4">
          {imagePreview ? (
            <img src={imagePreview} alt="Preview" className="rounded w-full" />
          ) : (
            <div className="w-full h-64 flex items-center justify-center text-muted">
              No image uploaded
            </div>
          )}
        </CardContent>

        <CardContent className="p-4 space-y-4">
          <Input type="file" accept="image/*" onChange={handleFileChange} />
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Waiting..." : "Submit"}
          </Button>
        </CardContent>
      </Card>

      {/* Result Section */}
      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <Card>
          <CardContent className="p-4">
            {processedImageUrl ? (
              <img src={processedImageUrl} alt="Result" className="rounded w-full" />
            ) : loading ? (
              <p className="text-muted">Processing image...</p>
            ) : (
              <p className="text-muted">No processed image returned.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            {loading ? (
              <p className="text-muted">Waiting for metadata...</p>
            ) : resultJson ? (
              <pre className="overflow-x-auto whitespace-pre-wrap text-sm bg-gray-900 text-white p-4 rounded">
                {JSON.stringify(resultJson, null, 2)}
              </pre>
            ) : (
              <p className="text-muted">Result metadata will appear here.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
