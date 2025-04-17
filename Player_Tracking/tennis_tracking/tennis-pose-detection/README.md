# 🎾 Tennis Pose Estimation: Understanding Player Movements  
[![ReadMe](https://img.shields.io/badge/ReadMe-018EF5?logo=readme&logoColor=fff)](#)
![Python](https://img.shields.io/badge/Python-3.10-blue)  
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-ff8f00?logo=tensorflow&logoColor=white)](#)

## 🧠 Overview
This project focuses on analyzing tennis player movements using pose estimation through a pretrained deep learning model. It detects key body joints, visualizes the skeletal structure, and calculates important angles between limbs, enabling a deeper understanding of player posture and movement patterns.

## ✨ Features
- **Pose Detection** using a pretrained TensorFlow-based model.
- **Joint Keypoint Extraction** from images of tennis players.
- **Skeleton Visualization** on both original and blank canvas.
- **Angle Calculation** between major body joints to analyze posture.
- **Highly Modular** code for easy experimentation.

## 📷 Demo Output

### Pose Detection and Skeleton Visualization
![pose demo](https://github.com/user-attachments/assets/f2cee88f-a5a9-497e-996c-a9400b1fee62)

_Sample output showing detected pose on a tennis player_

### Skeleton on Blank Canvas
![blank pose](https://github.com/user-attachments/assets/5d6c8848-bf71-499d-8286-5e1ae532d385)

_Clean skeletal structure on black background_

---

## 🧪 Try It Out
You can try this project on Google Colab or locally. Just follow the instructions below.

## 📦 Installation

### 🔧 Prerequisites
Make sure you have the following installed:
- Python 3.10+
- NumPy
- OpenCV
- TensorFlow (for pose model)

You can install dependencies using:
```bash
pip install numpy opencv-python tensorflow
```

### 🚀 Steps to Run
1. **Clone the Repository:**
```bash
git clone https://github.com/yourusername/tennis-pose-estimation.git
cd tennis-pose-estimation
```

2. **Download the Pose Model:**
Place the pretrained pose model file `pose.pb` inside your working directory or set its path in the script.

3. **Run the Script:**
You can either:
- Use the Colab Notebook (Recommended):  
  [Open in Google Colab](https://colab.research.google.com/drive/your-colab-link)

- Or run locally:
```bash
python pose_estimation.ipynb --input path_to_image.jpg --model pose.pb
```

---

## 📊 Keypoint & Skeleton Mapping

- **Keypoints Tracked:**
  - Head, Spine, Shoulders, Elbows, Hands, Hips, Knees, Feet, Eyes, Ears

- **Skeleton Connections:**  
  Connects key joints to visualize the player's pose as a skeletal structure.

---

## 📐 Angle Calculation
The following joint angles are calculated using 3-point geometry:
- Shoulder, Elbow, Wrist
- Hip, Knee, Foot
- Torso and Limb Angles (Spine-Shoulder, Spine-Hip)

This helps assess movement quality and form. Angles are annotated on the image automatically.

---

## ⚙️ Angle Formula

```python
def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
```

---

## 📁 Project Structure

```
├── pose_estimation.ipynb
├── pose.pb
├── input images
├── README.md
```

---

## 🧩 Challenges & Solutions

- **Model Accuracy:** Some joint detections are imprecise when limbs overlap.
    - ➤ Solution: Filter low-confidence keypoints and post-process output.
- **Overlapping Angle Text:** Annotated angles may overlap.
    - ➤ Solution: Dynamic offset system to reposition text intelligently.

---

## 🔮 Future Work

- Live video stream pose detection.
- Classification of shots/movements using angles and pose data.

---

## 🤝 Contributing

We welcome contributions! Please follow the standard contribution guidelines:

1. Fork the repository from [GitHub](https://github.com/HarshBhanot7/redback-orion).
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

## 👨‍💻 Contributors
- [*Harsh Bhanot*](https://github.com/HarshBhanot7)

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/Redback-Operations/redback-documentation/blob/main/LICENSE) file for details.

---

## 🙏 Acknowledgements
- TensorFlow and OpenCV communities.
- Pretrained model adapted from the OpenPose architecture.

