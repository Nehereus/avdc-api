FROM python:3.9-slim
LABEL org.opencontainers.image.source="https://github.com/Nehereus/avdc-api"

WORKDIR  /usr/src/app
COPY . .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV ENABLE_TRANSLATION=""
ENV TARGET_LANG=""
ENV DEEPL_API_KEY=""
ENV AVDC_DATABASE=""
ENV AVDC_TOKEN=""

ENV GOOGLE_APPLICATION_CREDENTIALS="/key.json"

ENV PORT=5000

CMD [ "python", "/usr/src/app/main.py" ]
