import cv2
import dlib
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from fatigue_detector import FatigueDetector

app = Flask(__name__)
CORS(app) # Mengizinkan React mengakses API ini

# Inisialisasi logika dan model
# (consecutive_frames dikurangi jadi 5 karena pengiriman via API web lebih lambat dari streaming lokal)
detector_logic = FatigueDetector(ear_threshold=0.25, consecutive_frames=5)
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)

# Jalur ini harus sama persis dengan yang ada di React (HF_API_URL)
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "Tidak ada gambar yang diterima"}), 400

        # 1. Menerima gambar base64 dari React dan mengubahnya menjadi format OpenCV
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 2. Proses Deteksi (Sama seperti sebelumnya)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray_frame, 0)

        status = "Aman (Alert)"
        ear_value = 0.0

        if len(faces) == 0:
            return jsonify({"ear": 0.0, "status": "Wajah tidak terdeteksi"})

        for face in faces:
            shape = landmark_predictor(gray_frame, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            leftEye = landmarks[lStart:lEnd]
            rightEye = landmarks[rStart:rEnd]

            ear_value, alarm_status = detector_logic.check_drowsiness(leftEye, rightEye)

            if alarm_status:
                status = "WARNING: DROWSY! (Ngantuk)"

        # 3. Mengembalikan nilai EAR dan Status ke React
        return jsonify({
            "ear": float(ear_value), 
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Port 7860 khusus untuk Hugging Face
    app.run(host='0.0.0.0', port=7860)