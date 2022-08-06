FROM public.ecr.aws/amazonlinux/amazonlinux:latest
ENV ServerName=web2048-site

RUN yum -y update && \
    yum -y install httpd unzip && \
    yum clean all

# Install app
COPY ./code/ /var/www/html/

# Config App
RUN echo "ServerName fargate.training " >> /etc/httpd/conf/httpd.conf

EXPOSE 80

ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]