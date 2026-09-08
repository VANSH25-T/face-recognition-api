# Face Recognition API

A powerful FastAPI-based REST API for face detection, recognition, and verification using Python and machine learning.

## Features

✨ **Face Detection** - Detect faces in images  
✨ **Face Recognition** - Recognize faces against a database of known faces  
✨ **Face Verification** - Verify if two images contain the same person  
✨ **Real-time Processing** - Fast inference using optimized models  
✨ **REST API** - Easy-to-use HTTP endpoints  
✨ **CORS Enabled** - Ready for frontend integration  

## Tech Stack

- **FastAPI** - Modern Python web framework
- **face-recognition** - Deep learning face recognition library
- **OpenCV** - Computer vision library
- **NumPy** - Numerical computing
- **Uvicorn** - ASGI web server

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/VANSH25-T/face-recognition-api.git
cd face-recognition-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Prepare known faces** (Optional)
   - Create a `known_faces/` directory
   - Create subdirectories for each person: `known_faces/person_name/`
   - Add face images (JPG format) to each directory
   ```
   known_faces/
   ├── john/
   │   ├── john1.jpg
   │   └── john2.jpg
   └── jane/
       ├── jane1.jpg
       └── jane2.jpg
   ```

## Running the API

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check
```http
GET /
```

Returns API status.

### 2. Detect Faces
```http
POST /api/detect-faces
Content-Type: multipart/form-data

file: <image_file>
```

**Response:**
```json
{
  "faces_detected": 2,
  "face_locations": [
    {"top": 50, "right": 150, "bottom": 200, "left": 100},
    {"top": 60, "right": 250, "bottom": 210, "left": 200}
  ]
}
```

### 3. Recognize Faces
```http
POST /api/recognize-faces
Content-Type: multipart/form-data

file: <image_file>
tolerance: 0.6  (optional, default: 0.6)
```

**Response:**
```json
{
  "matches": [
    {
      "name": "john",
      "confidence": 0.95,
      "distance": 0.05
    }
  ],
  "unknown_faces": 1
}
```

### 4. Verify Faces
```http
POST /api/verify-face
Content-Type: multipart/form-data

file1: <image_file_1>
file2: <image_file_2>
```

**Response:**
```json
{
  "match": true,
  "distance": 0.25,
  "confidence": 0.75
}
```

### 5. Reload Known Faces
```http
POST /api/reload-faces
```

Reload all faces from the `known_faces` directory.

### 6. Get Status
```http
GET /api/status
```

**Response:**
```json
{
  "status": "running",
  "known_faces_loaded": 5,
  "unique_people": 2,
  "people": ["john", "jane"]
}
```

## Usage Examples

### Using cURL

**Detect faces:**
```bash
curl -X POST "http://localhost:8000/api/detect-faces" \
  -F "file=@image.jpg"
```

**Recognize faces:**
```bash
curl -X POST "http://localhost:8000/api/recognize-faces" \
  -F "file=@image.jpg" \
  -F "tolerance=0.6"
```

**Verify two faces:**
```bash
curl -X POST "http://localhost:8000/api/verify-face" \
  -F "file1=@image1.jpg" \
  -F "file2=@image2.jpg"
```

### Using Python

```python
import requests

# Detect faces
with open("image.jpg", "rb") as f:
    response = requests.post("http://localhost:8000/api/detect-faces", files={"file": f})
    print(response.json())

# Recognize faces
with open("image.jpg", "rb") as f:
    response = requests.post("http://localhost:8000/api/recognize-faces", files={"file": f})
    print(response.json())

# Verify faces
with open("image1.jpg", "rb") as f1, open("image2.jpg", "rb") as f2:
    response = requests.post(
        "http://localhost:8000/api/verify-face",
        files={"file1": f1, "file2": f2}
    )
    print(response.json())
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:8000/api/recognize-faces", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Understanding Tolerance and Distance

- **Distance**: How different two faces are (0.0 = identical, 1.0 = completely different)
- **Tolerance**: Threshold for matching (default: 0.6)
  - Lower tolerance = stricter matching (fewer false positives)
  - Higher tolerance = looser matching (more false positives)
- **Confidence**: 1 - distance (higher = more confident)

Recommended tolerances:
- `0.4-0.5`: Very strict (recommended for security)
- `0.6`: Default (good balance)
- `0.8`: Loose (may get false positives)

## Project Structure

```
face-recognition-api/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Project dependencies
├── README.md              # This file
├── .gitignore             # Git ignore file
├── known_faces/           # Database of known faces
│   ├── person1/
│   └── person2/
└── uploaded_images/       # Temporary uploaded images
```

## Performance Tips

1. **Use JPG format** - Smaller file size, faster processing
2. **Optimize image size** - Use images around 640x480 or smaller
3. **GPU Support** - Install CUDA/cuDNN for faster processing
4. **Batch Processing** - Process multiple images at once
5. **Caching** - Known faces are loaded once at startup

## Troubleshooting

### Issue: "No known faces loaded"
**Solution:** 
- Create the `known_faces/` directory
- Add face images to subdirectories
- Call `/api/reload-faces` endpoint

### Issue: Poor recognition accuracy
**Solutions:**
- Use better quality images
- Ensure faces are clearly visible
- Add more sample images per person
- Adjust tolerance value (try 0.5-0.55)

### Issue: Slow inference
**Solutions:**
- Use smaller images
- Install GPU drivers for CUDA support
- Consider using faster detection model

## Deployment

### Docker
```bash
docker build -t face-recognition-api .
docker run -p 8000:8000 face-recognition-api
```

### Docker Compose
```bash
docker-compose up --build
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Face Recognition! 🎉**
