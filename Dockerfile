FROM python:3.10

RUN apt update && apt install gcc libespeak-dev ffmpeg -y

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import bertalign; bertalign.load_model()"

RUN python -c "import whisper; whisper.load_model('base')"

COPY ./ ./

RUN pip install ./

WORKDIR /work

ENTRYPOINT ["audiobooksyncer"]
