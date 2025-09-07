---
sidebar_position: 1
---
# Tennis Pose Estimation: Understanding Player Movements🎾 
[![ReadMe](https://img.shields.io/badge/ReadMe-018EF5?logo=readme&logoColor=fff)](#)
![Python](https://img.shields.io/badge/Python-3.10-red)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-purple)
![COCO](https://img.shields.io/badge/COCO-green)

## 🧠 Overview
This project focuses on analyzing tennis player movements using pose estimation through a pretrained OpenPose model (using OpenCV's DNN module). It detects key body joints, visualizes the skeletal structure, and calculates important angles between limbs, enabling a deeper understanding of player posture and movement patterns.

## ✨ Features
- **Pose Detection** using a pretrained OpenPose model with OpenCV.
- **Joint Keypoint Extraction** from static images of tennis players.
- **Skeleton Visualization** on both the original image and a blank canvas.
- **Angle Calculation** between major body joints to analyze posture.
- **Highly Modular** code for easy experimentation and extension.

## 📷 Demo Output

### 🧍‍♂️ Pose Detection and Skeleton Visualization

<p align="center">
  <img src="https://github.com/user-attachments/assets/dc6f0ca1-272c-4574-b805-6f35e35f4887" width="500"/>
  <img src="https://github.com/user-attachments/assets/b168ee1d-48e7-49e9-954f-d979ffc661d1" width="500"/>
  <img src="https://github.com/user-attachments/assets/7bfda739-6942-4755-a2d3-3a02cb84c06d" width="500"/>
  <img src="https://github.com/user-attachments/assets/ea74b9ba-01fd-4bb8-857d-f18f3723c79d" width="500"/>
  <img src="https://github.com/user-attachments/assets/b8afc82e-081b-4b05-8e70-4d6971e02f66" width="500"/>
</p>

<p align="center"><i>Sample outputs showing detected keypoints and full-body pose on tennis players</i></p>

---

### 🎯 Skeleton on Blank Canvas

<p align="center">
  <img src="https://github.com/user-attachments/assets/5917f9b2-baa1-4a3d-bd38-78dee8a7efaa" width="500"/>
  <img src="https://github.com/user-attachments/assets/14ed2280-2a63-4543-9378-aadcad28bc66" width="500"/>
  <img src="https://github.com/user-attachments/assets/02833a6c-9e96-4166-8fd0-68ad5dcc8430" width="500"/>
  <img src="https://github.com/user-attachments/assets/8b9d0604-81b4-4f2b-bce2-dd8a69dcf42d" width="500"/>
  <img src="https://github.com/user-attachments/assets/a9d671d3-c9f9-4706-90d2-a2c631f4383d" width="500"/>
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

You can install dependencies using:
```bash
pip install numpy opencv-python
```

### 🚀 Steps to Run
1. **Clone the Repository:**
```bash
git clone "https://github.com/HarshBhanot7/redback-orion.git"
cd tennis-pose-estimation
```

2. **Download the Pose Model Files:**
[From here](https://drive.google.com/drive/folders/1erlXdp3oJEjQehdIhnbcNig_0vClxxSF?usp=sharing) and place them into your working directory:
- `pose_deploy_linevec.prototxt`
- `pose_iter_440000.caffemodel`

3. **Run the Script:**
If using Google Colab:
- Open the notebook and upload your images and models.

If running locally:
```bash
python pose_estimation.ipynb
```
or run it cell-by-cell in Jupyter Notebook.

---

## 📁 Project Structure

```
├── Pose Detection.ipynb
├── pose_deploy_linevec.prototxt
├── pose_iter_440000.caffemodel
├── Input Images/
├── Output Images/
├── README.md
```

---

## 📊 Keypoint & Skeleton Mapping

- **Keypoints Tracked:**
  - Nose, Neck, Shoulders, Elbows, Wrists, Hips, Knees, Ankles, Eyes, Ears

- **Skeleton Connections:**  
  Connects key joints to visualize the player's pose as a skeletal structure.

---

## 📐 Angle Calculation
The following joint angles are calculated using 3-point geometry:
- Shoulder-Elbow-Wrist
- Hip-Knee-Ankle
- Neck-Shoulder-Elbow
- Neck-Hip-Knee
- Torso Width (Shoulder to Shoulder) and Hip Width (Hip to Hip)

Angles are annotated on the image and also printed in the console output for logging or debugging purposes.

---

## ⚙️ Angle Formula

```python
def calculate_angle(a, b, c):
    """
    Calculate the angle between three points (in degrees).
    
    Parameters:
        a, b, c: Points in the form of (x, y) coordinates
                 b is the vertex point
    
    Returns:
        angle: The angle in degrees
    """
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
```

---

## 📐 Angle Calculation Output

### Angle Estimation with High Accuracy

<p align="center">
  <img src="https://github.com/user-attachments/assets/1ef94ecc-fa18-4f71-b818-b7bea35742ab" width="500"/>
  <img src="https://github.com/user-attachments/assets/c4fcbf9e-25db-4ad1-b693-06634d8c1115" width="500"/>
  <img src="https://github.com/user-attachments/assets/72f0fd83-9a3c-4b78-aba6-1b459840a997" width="500"/>
  <img src="https://github.com/user-attachments/assets/d9484c1b-0be7-431b-a30e-80030f28f762" width="500"/>
  <img src="https://github.com/user-attachments/assets/eaabb285-a6c7-4940-9f6e-5805efde8f82" width="500"/>
</p>

<p align="center"><i>Angles between joints (e.g., elbow, knee) are annotated to analyze player posture.</i></p>

---

## 💻 Console Output Example

```
RShoulder-RElbow-RWrist: 153°
LShoulder-LElbow-LWrist: 147°
RHip-RKnee-RAnkle: 168°
LHip-LKnee-LAnkle: 164°
Neck-RShoulder-RElbow: 132°
Neck-LShoulder-LElbow: 135°
RShoulder-Neck-LShoulder: 95°
RHip-Neck-LHip: 101°
```
These printed values help with:
- Debugging pose estimation
- Logging joint angles for further analysis
- Verifying correctness without needing to inspect images

---

## 🧩 Challenges & Solutions

| **Challenge**         | **Solution**                                                             |
|-----------------------|--------------------------------------------------------------------------|
| **Model Accuracy**     | Filtered low-confidence detections & applied post-processing             |
| **Text Overlap**       | Implemented dynamic text positioning algorithm                           |
| **Occlusion Handling** | Developed interpolation for temporarily hidden joints                    |

---

## 🔮 Future Work

- Pose Comparison Feature: Implement functionality to compare a player’s pose side-by-side with that of a professional. Highlight key differences in joint angles to help players visually identify areas for improvement.
- Technique Scoring System: Develop an automated scoring system that evaluates the player's form by comparing joint angles to an ideal reference. This can help players track their technique accuracy and progress over time.
- Injury Risk Alerts: Integrate a system that analyzes joint angle data to detect potentially harmful or incorrect movements. Provide real-time alerts or warnings to help prevent injuries and promote safe training practices.

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
- [Harsh Bhanot](https://github.com/HarshBhanot7) - *Project Lead & Developer*

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/Redback-Operations/redback-documentation/blob/main/LICENSE) file for details.

---

## 🙏 Acknowledgements
- OpenCV and OpenPose community for providing the pretrained models.
- Pretrained model adapted from the OpenCV architecture.

---

[🔼 Back to Top](#tennis-pose-estimation-understanding-player-movements)
