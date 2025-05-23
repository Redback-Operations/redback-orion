import cv2
import numpy as np


def calculateHomography(ptsSRC, ptsDST):
    return cv2.findHomography(ptsSRC, ptsDST)[0]


def transformPoints(points, homographyMatrix):
    points = np.concatenate([points, np.ones((points.shape[0], 1))], axis=1)
    transformedPoints = homographyMatrix.dot(points.T).T
    transformedPoints /= transformedPoints[:, 2][:, np.newaxis]
    return transformedPoints[:, :2]
