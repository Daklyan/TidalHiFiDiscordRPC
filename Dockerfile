FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ARG USER=appuser
ARG UID=1000
RUN adduser --uid ${UID} --disabled-password --gecos "" ${USER}
RUN chown -R ${USER}:${USER} /app

USER ${USER}

CMD ["sh", "-c", "python -X utf8 main.py & tail -f /dev/null"]
