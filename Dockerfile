FROM debian:latest

MAINTAINER Mike iLL <mike@mzoo.org>

USER root

RUN apt-get update && apt-get install -y \
  adduser \
	debianutils \
	fortune-mod \
	fortunes-min \
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

# Copy qm-vamp-plugins.so, qm-vamp-plugins.cat and
#               qm-vamp-plugins.n3 to $HOME/vamp/ or /usr/local/lib/vamp/
#               or /usr/lib/vamp/