# 1. Gunakan sistem operasi Python bawaan yang ringan
FROM python:3.10-slim

# 2. Atur folder kerja di dalam server
WORKDIR /app

# 3. Install aplikasi sistem yang dibutuhkan C++ dan OpenCV beserta update keamanannya
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential \
    cmake \
    curl \
    bzip2 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. TRIK RAHASIA: Download model dlib langsung dari internet saat build!
RUN curl -L -o shape_predictor_68_face_landmarks.dat.bz2 https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2 \
    && bzip2 -d shape_predictor_68_face_landmarks.dat.bz2

# 5. Install library Python dari requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Masukkan semua kodingan backend kamu ke server
COPY . .

# 7. Buka akses port 7860 untuk Hugging Face
EXPOSE 7860

# 8. Jalankan server Flask
CMD ["python", "main.py"]