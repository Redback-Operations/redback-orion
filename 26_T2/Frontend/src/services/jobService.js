export const pollJob = (jobId, token, callbacks) => {
  const interval = setInterval(async () => {
    const res = await fetch(
      `http://localhost:8000/status/${jobId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    const data = await res.json()

    if (data.status !== "processing") {
      clearInterval(interval)

      if (data.status === "done" || data.status === "partial") {
        callbacks.onSuccess?.(data)
      } else {
        callbacks.onError?.(data)
      }
    }
  }, 3000)
}