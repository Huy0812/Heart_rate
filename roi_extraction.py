import cv2
import mediapipe as mp
import numpy as np


class RoIExtraction():
    forehead_roi = 0
    nose_roi = 0
    face_roi = 0

    def __init__(self):

        # Arrays are list of landmark for each RoI location

        self.forehead_arr = [105, 103, 67, 109, 10, 338, 297, 332, 334, 105]
        self.nose_arr = [94, 206, 50, 118, 6, 347, 280, 426, 94]
        self.face_arr = [10, 338, 297, 332, 284, 251, 389, 356, 454, 366, 376, 411, 426, 94, 206, 187, 147, 137, 234,
                         127, 162, 21, 54, 103, 67, 109, 10]
        self.outline_forehead = []
        self.outline_nose = []
        self.outline_face = []

    def __call__(self, image):
        self.roi_extraction(image)

    def setForehead_roi(self, forehead_roi):
        self.forehead_roi = forehead_roi

    def getForehead_roi(self):
        return self.forehead_roi

    def setNose_roi(self, nose_roi):
        self.nose_roi = nose_roi

    def getNose_roi(self):
        return self.nose_roi

    def setFace_roi(self, face_roi):
        self.face_roi = face_roi

    def getFace_roi(self):
        return self.face_roi

    def roi_extraction(self, image):
        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            results = face_mesh.process(image)
            mask_forehead, self.outline_forehead = self.create_mask(results, self.forehead_arr, image)
            mask_nose, self.outline_nose = self.create_mask(results, self.nose_arr, image)
            mask_face, self.outline_face = self.create_mask(results, self.face_arr, image)
            self.setForehead_roi(mask_forehead)
            self.setNose_roi(mask_nose)
            self.setFace_roi(mask_face)

            # Extraction RoI from Image using landmarks of mediapipe Face Detection

    def create_mask(self, results, roi_arr, image):
        outline = []

        if results.multi_face_landmarks:

            for face_landmarks in results.multi_face_landmarks:
                count = 0

                while count < len(roi_arr):
                    temp = roi_arr[count]

                    # Nomarlize landmark to pixels coordinates

                    x = face_landmarks.landmark[temp].x
                    y = face_landmarks.landmark[temp].y
                    shape = image.shape
                    relative_x = int(x * shape[1])
                    relative_y = int(y * shape[0])

                    # add pixels coordinates to array

                    outline.append((relative_x, relative_y))
                    count = count + 1

        # Using pixels coordinates array to create mask

        mask = np.zeros((image.shape[0], image.shape[1]))
        mask = cv2.fillConvexPoly(mask, np.array(outline), 1)
        mask = mask.astype(np.bool_)
        return mask, outline
