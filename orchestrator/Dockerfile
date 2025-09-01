
FROM python:3.11-slim
WORKDIR /workspace
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /workspace/
CMD ["python", "workflow.py"]
