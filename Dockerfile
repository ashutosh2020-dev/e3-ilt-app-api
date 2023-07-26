FROM python:3.9

WORKDIR /dockerworkdir

COPY ./app /dockerworkdir/app
COPY ./.ebextensions /dockerworkdir/.ebextensions
COPY ./certs /dockerworkdir/certs
COPY requirements.txt /dockerworkdir/
COPY main.py /dockerworkdir/
COPY README.md  /dockerworkdir/
COPY ilt_db.db  /dockerworkdir/

RUN  pip install --no-cache-dir --upgrade pip && \
     pip install --no-cache-dir -r requirements.txt

EXPOSE 443

CMD ["python", "main.py"]
