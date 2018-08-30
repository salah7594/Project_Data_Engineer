FROM python:3

RUN mkdir /home/scrapy/
WORKDIR /home/scrapy/

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["scrapy"]
CMD ["crawl", "authors"]
