FROM nginx:1.27-alpine
COPY index.html data.js facts.js quiz.js /usr/share/nginx/html/
COPY flags /usr/share/nginx/html/flags
