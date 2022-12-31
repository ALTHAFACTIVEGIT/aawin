
# pull official base image
FROM python:3.8

RUN mkdir -p /opt/pip_cache
RUN mkdir -p /opt/aavin-assets && chmod -R 777 /opt/

# set work directory
WORKDIR /opt/aavin-admin

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

#EXPOSE 8000

CMD ["python manage.py migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
