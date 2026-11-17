FROM nginx

RUN apt update
RUN apt install tor -y
RUN printf "HiddenServiceDir /var/lib/tor/my_website/\n" >> /etc/tor/torrc
RUN printf "HiddenServicePort 80 127.0.0.1:8080\n" >> /etc/tor/torrc
RUN systemctl restart tor

COPY index.html /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# docker build -t some-content-nginx .                         
# docker run --name some-nginx -d -p 8080:80 some-content-nginx
# docker stop some-nginx && docker rm some-nginx && docker rmi some-content-nginx:latest
