FROM fike/debian:jessie.en_US
# https://github.com/fike/dockerfiles/blob/master/postgres/9.2/Dockerfile
MAINTAINER Mike iLL <mike@mzoo.org>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq &&       apt-get upgrade -y

RUN apt-get install --no-install-recommends wget -y

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main 9.2" > /etc/apt/sources.list.d/pgdg.list

RUN gpg --keyserver keys.gnupg.net --recv-keys ACCC4CF8

RUN gpg --export --armor ACCC4CF8|apt-key add -

RUN apt-get update -qq &&       apt-get upgrade -y

RUN apt-get install --no-install-recommends -y \ 
      postgresql-9.2       postgresql-client-9.2 

RUN apt-get clean &&       apt-get autoremove --purge -y &&       rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER root

RUN apt-get update && apt-get install -y \
  adduser \
	debianutils \
	fortune-mod \
	fortunes-min \
	git \ 
	lame \
	python-pip \
	python-numpy \ 
	python-scipy \ 
	python-matplotlib \
	ipython \
	ipython-notebook \
	python-pandas \
	python-sympy \
	python-nose \
	sudo \
	vim \
	wget \
	sonic-visualiser
	
	# sonic-annotator_1.4cc1-1_amd64.deb ?
	
# Make ssh dir
RUN mkdir /root/.ssh/

# Copy over private key, and set permissions
ADD id_rsa /root/.ssh/id_rsa

# Create known_hosts
RUN touch /root/.ssh/known_hosts
# Add github key
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

RUN wget https://code.soundsoftware.ac.uk/attachments/download/1602/qm-vamp-plugins-linux64-v1.7.1.tar.bz2 \
 && tar xvjf qm-vamp-plugins-linux64-v1.7.1.tar.bz2
 
CMD cd qm-vamp-plugins-linux64-v1.7.1 && \
	mkdir /usr/lib/vamp && \
	cp qm-* /usr/lib/vamp && \
		cd ../

RUN wget http://code.soundsoftware.ac.uk/attachments/download/670/vampy-2.0-amd64-linux.tar.bz2 \
 && tar xvjf vampy-2.0-amd64-linux.tar.bz2

CMD cd vampy-2.0-amd64-linux
 
CMD echo "Maybe that worked."

CMD cp -r Example\ VamPy\ plugins/ /usr/lib/vamp

# Clone the repo into the docker container
RUN git clone git@github.com:MikeiLL/appension.git

# Enter the repo directory
CMD cd appension

# Install requirements with pip
RUN pip install -r requirements.txt

# Copy qm-vamp-plugins.so, qm-vamp-plugins.cat and
#               qm-vamp-plugins.n3 to $HOME/vamp/ or /usr/local/lib/vamp/
#               or /usr/lib/vamp/

RUN /etc/init.d/postgresql start &&       su postgres -c "psql --command \"ALTER USER postgres with password 'foobar';\" "

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.2/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.2/main/postgresql.conf

EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

CMD ["/usr/lib/postgresql/9.2/bin/postgres", "-D", "/var/lib/postgresql/9.2/main", "-c", "config_file=/etc/postgresql/9.2/main/postgresql.conf"]

# Run the server
python -m fore.server
