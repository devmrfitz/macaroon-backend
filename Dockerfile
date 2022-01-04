FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app


COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x ./utils/run.sh
RUN ln -s /run/shm /dev/shm


EXPOSE 80
ENTRYPOINT ["utils/run.sh"]
