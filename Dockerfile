# Import Ubuntu
FROM ubuntu:20.04

# Make /app dir
RUN mkdir /app
WORKDIR /app

# Installation of Requirements
COPY . .

RUN apt update && apt install -y --no-install-recommends git python3 python3-pip mkvtoolnix ffmpeg
RUN pip3 install --no-cache-dir -r requirements.txt


# Start bot
CMD ["bash", "run.sh"]
