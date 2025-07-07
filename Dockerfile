# 1️⃣ Use an official Ubuntu base image
FROM ubuntu:22.04

# 2️⃣ Install Python 3.10 and pip
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-distutils python3-pip && \
    rm -rf /var/lib/apt/lists/*

# 3️⃣ Set the working directory
WORKDIR /app

# 4️⃣ Copy only requirements first (for Docker layer caching)
COPY requirements.txt .

# 5️⃣ Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# 6️⃣ Copy the rest of your project into /app
COPY . .

# 7️⃣ Expose port 8000
EXPOSE 8000

# 8️⃣ Run your FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]