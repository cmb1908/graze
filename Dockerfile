# Use an official Python runtime as a parent image
#FROM python:3.6-slim
FROM sunhawk2100/dockselpy

WORKDIR /usr/src/app/
COPY requirements.txt /usr/src/app/
#COPY . /usr/src/app/

run pip3 install --upgrade pip
RUN apt-get -yq install zlib1g-dev libjpeg-dev tesseract-ocr
RUN pip3 install -r requirements.txt
RUN pip3 install --index-url https://test.pypi.org/simple/ graze
#RUN python3 setup.py install

# Run graze when the container launches
CMD ["bash"]
