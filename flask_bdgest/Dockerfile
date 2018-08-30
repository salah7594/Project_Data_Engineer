FROM python:3

RUN mkdir /home/flask/
WORKDIR /home/flask/

COPY . . 

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python"]
CMD ["run.py"]
