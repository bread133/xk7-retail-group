import cv2
import numpy as np

def preprocess_video(video_path, width=144, height=176, fps=4):
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Применение гауссовского сглаживания
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        # Изменение размера
        frame = cv2.resize(frame, (width, height))
        frames.append(frame)
    
    cap.release()
    
    # Децимация по времени
    downsampled_frames = frames[::int(cap.get(cv2.CAP_PROP_FPS) / fps)]
    
    return downsampled_frames 