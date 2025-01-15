FROM python:3.12

WORKDIR /code



COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt


COPY ./app /code

ENV PYTHONPATH=/code
RUN pip install "fastapi[standard]"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
