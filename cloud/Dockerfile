# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim
RUN apt-get update && apt-get install -y iproute2
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8081
#ENTRYPOINT [ "python" ]
CMD ["python", "cloud.py"]