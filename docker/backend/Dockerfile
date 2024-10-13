FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/star-burger

COPY requirements.txt /opt/star-burger/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /opt/star-burger/

EXPOSE 8080

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "star_burger.wsgi:application"]
