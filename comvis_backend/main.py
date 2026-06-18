import cv2
import dlib
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from fatigue_detector import FatigueDetector

app = Flask(__name__)
CORS(app)


detector_logic = FatigueDetector(
    ear_drowsy=0.23, 
    ear_warning=0.25, 
    mar_threshold=0.6,   
    consecutive_frames=9
)

face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "Tidak ada gambar yang diterima"}), 400

        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Biarkan 1 agar wajahmu lebih gampang terdeteksi di resolusi HD
        faces = face_detector(gray_frame, 1)

        status_text = "Aman (Alert)"
        ear_value = 0.0
        mar_value = 0.0

        if len(faces) == 0:
            return jsonify({
                "ear": 0.0, 
                "status": "Wajah terhalang / Tidak terdeteksi", 
                "image": data['image'] 
            })

        for face in faces:
            shape = landmark_predictor(gray_frame, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            rightEye = landmarks[36:42]
            leftEye = landmarks[42:48]
            mouth = landmarks[48:68]

            avg_ear, mar, status_code = detector_logic.check_drowsiness(leftEye, rightEye, mouth)

            # Warna kotak (BGR format di OpenCV)
            color = (0, 255, 0) # Hijau untuk AMAN
            if status_code == 10:
                status_text = "BAHAYA: DROWSY! (Ngantuk)"
                color = (0, 0, 255) # Merah untuk BAHAYA
            elif status_code == 5:
                status_text = "WARNING: Mulai Lelah / Menguap"
                color = (0, 255, 255)


            cv2.drawContours(frame, [np.array(leftEye)], -1, color, 1)
            cv2.drawContours(frame, [np.array(rightEye)], -1, color, 1)
            cv2.drawContours(frame, [np.array(mouth)], -1, color, 1)
            
            ear_value = avg_ear
            mar_value = mar

        _, buffer = cv2.imencode('.jpg', frame)
        processed_image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            "ear": float(ear_value), 
            "mar": float(mar_value),
            "status": status_text,
            "image": processed_image_base64, 
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860)