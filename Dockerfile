FROM nginx:1.27-alpine
COPY index.html data.js /usr/share/nginx/html/
