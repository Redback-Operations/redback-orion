# Field and Object Detection Project Documentation

![Readme style: standard](https://img.shields.io/badge/readme%20style-standard-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)

## Overview

This project focused on detecting objects(players, ball, goalkeeper, referee), as well as detecting key points within a soccer pitch. The end-goal of which is to create a 2D transformation of the image of the field and to positions of the different objects via homography. This transformation is then used in calculating the expected goal (XG) of a specific shot. 

## Object Detection and Field Detection Model

The object detection model utilizes a pre-trained model. This would not have been possible without:
1. **Object Detection**: https://universe.roboflow.com/roboflow-jvuqo/football-players-detection-3zvbc/model/12
2. **Field Detection**: https://universe.roboflow.com/roboflow-jvuqo/football-field-detection-f07vi/model/15

I attempted to train myself with the same dataset, but could not achieve nearly the same amount of accuracy.

## How does it work?

1. **Image Input**: Accept an image or frame from a soccer match video.
2. **Annotated Image**: Detect and annotate objects (players, ball, etc.) and key points on the pitch.
3. **2D Transformation**: Perform homography to transform the annotated image to a 2D plane.
4. **XG Calculation**: Calculate the expected goal (XG) based on the positions and actions captured in the 2D transformation.

## Example

- ![Image](https://i.ibb.co/YyyMsrC/image.png)
- ![Annotated Image](https://i.ibb.co/9whmLhj/annotated.png)
- ![Transformed Image](https://i.ibb.co/Rggn96K/transformed.png)


## Prerequsites
- 'cv2'
- 'numpy'
- 'supervision'
- 'inference'
- 'dataclasses'
- 'typing'
- 'matplotlib'
- 'collections'


## Future Work

The integration of the XG Model is still in progress. 

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository.**
2. **Create a new branch:**
   ```bash
   git checkout -b feature-branch
   ```
3. **Make your changes and commit them:**
   ```bash
   git commit -m 'Add new feature'
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature-branch
   ```
5. **Open a pull request.**

## Contributors

- [Miguel Marabut](https://github.com/MigsMarabut)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- **OpenCV and Computer Vision Communities**: For their extensive work in computer vision and object detection.
- **Soccer Analytics Research**: Contributions to the field of sports analytics that inspired parts of this project.

