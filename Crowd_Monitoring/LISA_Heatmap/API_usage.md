
---
# Crowd Density API – Usage Guide

This API processes uploaded video frames (images) and returns:  
- **Estimated people count** in the stands (via CSRNet + LISASegmentor).  
- **Heatmap image** (PNG format) showing density distribution.  

---

## Base URL
http://localhost:8000

## Endpoint

### `POST /analyze_frame/`

Analyzes a single uploaded image frame.  

---

## Headers

- **Response headers**
  - `People-Count`: integer value (estimated number of people in the frame).

---

## Input Requirements

- **Method:** `POST`  
- **Content-Type:** `multipart/form-data`  
- **Form field:** `file` (the uploaded image).  
- **Supported formats:** `.jpg`, `.jpeg`, `.png`  
- **Image type:** RGB (will be auto-converted if not)  

---

## Request Body

Form-data with a single image file:

| Key   | Type | Description                        |
|-------|------|------------------------------------|
| file  | file | Image frame (PNG/JPG) to analyze. |

---

## Response

- **200 OK**
  - **Content-Type:** `image/png`
  - **Body:** Heatmap image (PNG)  
  - **Headers:** `People-Count: <int>`  
---

## Example Usage

### cURL

```bash
curl -X POST "http://localhost:8000/analyze_frame/" \
  -H "accept: image/png" \
  -F "file=@frame_10.jpg" \
  -o output_heatmap.png \
  -D headers.txt
