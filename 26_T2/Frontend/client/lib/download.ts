/**
 * Safely downloads a file by creating a temporary anchor element
 * and cleaning it up properly to prevent DOM manipulation errors
 */
export function downloadFile(
  content: string | Blob,
  filename: string,
  mimeType: string = "text/plain",
): void {
  try {
    const blob =
      content instanceof Blob
        ? content
        : new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = filename;
    a.style.display = "none";

    try {
      document.body.appendChild(a);
      a.click();
    } finally {
      // Safely remove the element
      if (a.parentNode) {
        a.parentNode.removeChild(a);
      }
      URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error("Download failed:", error);
    // Fallback: try to open in new window
    if (content instanceof Blob) {
      const url = URL.createObjectURL(content);
      const newWindow = window.open(url, "_blank");
      if (newWindow) {
        // Clean up URL after a delay
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      }
    }
  }
}

/**
 * Downloads JSON data as a file
 */
export function downloadJSON(data: any, filename: string): void {
  const content = JSON.stringify(data, null, 2);
  downloadFile(
    content,
    filename.endsWith(".json") ? filename : `${filename}.json`,
    "application/json",
  );
}

/**
 * Downloads CSV data as a file
 */
export function downloadCSV(data: string, filename: string): void {
  downloadFile(
    data,
    filename.endsWith(".csv") ? filename : `${filename}.csv`,
    "text/csv",
  );
}

/**
 * Downloads text content as a file
 */
export function downloadText(content: string, filename: string): void {
  downloadFile(
    content,
    filename.endsWith(".txt") ? filename : `${filename}.txt`,
    "text/plain",
  );
}

/**
 * Hook for handling downloads in React components
 */
export function useDownload() {
  const handleDownload = (
    content: string | Blob,
    filename: string,
    mimeType?: string,
  ) => {
    downloadFile(content, filename, mimeType);
  };

  const downloadJSON = (data: any, filename: string) => {
    const content = JSON.stringify(data, null, 2);
    handleDownload(
      content,
      filename.endsWith(".json") ? filename : `${filename}.json`,
      "application/json",
    );
  };

  const downloadCSV = (data: string, filename: string) => {
    handleDownload(
      data,
      filename.endsWith(".csv") ? filename : `${filename}.csv`,
      "text/csv",
    );
  };

  const downloadText = (content: string, filename: string) => {
    handleDownload(
      content,
      filename.endsWith(".txt") ? filename : `${filename}.txt`,
      "text/plain",
    );
  };

  return {
    download: handleDownload,
    downloadJSON,
    downloadCSV,
    downloadText,
  };
}
