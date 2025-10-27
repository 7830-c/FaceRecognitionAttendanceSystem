# Use official lightweight Python 3.13 image
FROM python:3.13-slim

# Install system dependencies required by OpenCV, dlib, and general builds
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    cmake \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8501

# ✅ This dynamically uses Railway's assigned port
CMD bash -c 'streamlit run Home.py --server.port=${PORT:-8501} --server.address=0.0.0.0'
