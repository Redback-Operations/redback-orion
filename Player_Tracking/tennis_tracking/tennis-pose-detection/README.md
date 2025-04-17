# 🎾 Tennis Pose Estimation: Understanding Player Movements  
[![ReadMe](https://img.shields.io/badge/ReadMe-018EF5?logo=readme&logoColor=fff)](#)
![Python](https://img.shields.io/badge/Python-3.10-grey)  

![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-8f00ff?logo=tensorflow&logoColor=white)](#)

## 🧠 Overview
This project focuses on analyzing tennis player movements using pose estimation through a pretrained deep learning model. It detects key body joints, visualizes the skeletal structure, and calculates important angles between limbs, enabling a deeper understanding of player posture and movement patterns.

## ✨ Features
- **Pose Detection** using a pretrained TensorFlow-based model.
- **Joint Keypoint Extraction** from images of tennis players.
- **Skeleton Visualization** on both original and blank canvas.
- **Angle Calculation** between major body joints to analyze posture.
- **Highly Modular** code for easy experimentation.

## 📷 Demo Output

### 🧍‍♂️ Pose Detection and Skeleton Visualization

<p align="center">
  <img src="https://github.com/user-attachments/assets/f2cee88f-a5a9-497e-996c-a9400b1fee62" width="470"/>
  <img src="https://github.com/user-attachments/assets/56ec4397-3b77-4139-a885-a5918f7aad90" width="400"/>
  <img src="https://github.com/user-attachments/assets/740443e8-9132-4622-9b69-0afd140edf94" width="500"/>
</p>

<p align="center"><i>Sample outputs showing detected keypoints and full-body pose on tennis players</i></p>

---

### 🎯 Skeleton on Blank Canvas

<p align="center">
  <img src="https://github.com/user-attachments/assets/5d6c8848-bf71-499d-8286-5e1ae532d385" width="450"/>
  <img src="https://github.com/user-attachments/assets/0ede28b1-3aa8-455d-ad6d-638a0f8c29c2" width="400"/>
  <img src="https://github.com/user-attachments/assets/7943af2d-67d6-402c-8b40-6985ee889fd4" width="550"/>
</p>

<p align="center"><i>Clean visualization of skeleton structure without background distractions</i></p>


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

## 📐 Angle Calculation Output

### Visualizing Pose and Angle Estimation on a Tennis Player 
![angle demo](https://github.com/user-attachments/assets/936a9fa3-2264-4386-a6b0-7b2ca2e8ed25)


_Angles between joints (e.g. elbow, knee) are annotated on the image to analyze posture_

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

1. Fork the repository from [GitHub](https://github.com/HarshBhanot7/redback-orion)
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

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

