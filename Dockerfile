FROM python:3.13-alpine
RUN adduser -D -H game && mkdir -p /app /data && chown game /data
COPY server.py index.html data.js facts.js quiz.js /app/
COPY flags /app/flags
ENV BLANK_MAP_HOST=0.0.0.0 BLANK_MAP_PORT=8770 BLANK_MAP_DB=/data/blank-map.sqlite
USER game
VOLUME /data
EXPOSE 8770
CMD ["python", "/app/server.py"]
