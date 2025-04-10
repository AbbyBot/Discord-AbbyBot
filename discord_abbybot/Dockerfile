FROM python:3.13.2-slim
COPY . .
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "abbybot.py"]