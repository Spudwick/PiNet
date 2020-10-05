FROM balenalib/raspberry-pi-debian:buster

# Set working directory.
WORKDIR /srv/gitlab

# Install.
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install curl openssh-server ca-certificates apt-transport-https
RUN curl https://packages.gitlab.com/gpg.key | apt-key add -
RUN curl -sS https://packages.gitlab.com/install/repositories/gitlab/raspberry-pi2/script.deb.sh | bash
RUN apt-get install gitlab-ce

# Copy in Gitlab config file.
COPY ./gitlab.rb /etc/gitlab/gitlab.rb
RUN chmod 644 /etc/gitlab/gitlab.rb
RUN chown root:root /etc/gitlab/gitlab.rb

# TODO: Actually start GitLab in a way that isn't borked by container'isation.

# Expose ports required for GitLab.
EXPOSE 80
EXPOSE 443
EXPOSE 22
