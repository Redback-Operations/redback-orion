export const uploadVideo = (file, token, onProgress) => {
  return new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append("file", file)

    const xhr = new XMLHttpRequest()

    xhr.open("POST", "http://localhost:8000/upload")

    xhr.setRequestHeader("Authorization", `Bearer ${token}`)

    // upload progress
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100)
        onProgress(percent)
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(new Error("Upload failed"))
      }
    }

    xhr.onerror = () => {
      reject(new Error("Network error"))
    }

    xhr.send(formData)
  })
}