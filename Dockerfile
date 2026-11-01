FROM nginx:1.27-alpine
COPY index.html data.js facts.js /usr/share/nginx/html/
