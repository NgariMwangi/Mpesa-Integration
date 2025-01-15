FROM tiangolo/uwsgi-nginx-flask:python3.12

WORKDIR /code



COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt


COPY . /code

ENV PYTHONPATH=/code
RUN pip install "fastapi[standard]"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
