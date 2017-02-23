#
# A sample docker file generated using 
#  ./Simple_Prep_docker jessie 20150306T060524Z 
# using 1.0.0 version of the scripts
#
FROM neurodebian:jessie
MAINTAINER Yaroslav Halchenko <debian@onerussian.com>

USER root

# Speed up installation using our apt cacher - modify conf/etc/apt/apt.conf.d/99apt-cacher if you have any
RUN mkdir -p /etc/apt/apt.conf.d/
COPY conf/etc/apt/apt.conf.d/99apt-cacher /etc/apt/apt.conf.d/99apt-cacher
RUN chmod a+r /etc/apt/apt.conf.d/99apt-cacher

# Make deb-src avail
# RUN sed -i -e 's,^deb\(.*\),deb\1\ndeb-src\1,g' /etc/apt/sources.list.d/neurodebian.sources.list /etc/apt/sources.list

# Make contrib and non-free avail for FSL
RUN sed -i -e 's, main$, main contrib non-free,g' /etc/apt/sources.list.d/neurodebian.sources.list

# Assure popcon doesn't kick in
RUN bash -c "echo 'debconf debconf/frontend select noninteractive' | debconf-set-selections -"

RUN apt-get update
# Use bash for extended syntax
RUN apt-get install -y -q eatmydata
# Some rudimentary tools if we need to do anything within docker and curl and unzip needed for setting up conda
RUN bash -c "eatmydata apt-get install -y -q vim less man-db curl unzip bzip2"
# Run additional lines, primarily to setup/enable snapshots repository etc
RUN bash -c "sed -i -e 's,http://neuro.debian.net/debian/* ,http://snapshot-neuro.debian.net:5002/archive/neurodebian/20150306T060524Z/ ,g' etc/apt/sources.list.d/neurodebian.sources.list;"
RUN bash -c "curl -s http://neuro.debian.net/_files/knock-snapshots;"
RUN bash -c "eatmydata apt-get update; eatmydata apt-get dist-upgrade -y;"
# Install fsl-complete
#RUN bash -c "eatmydata apt-get install -y -q fsl-complete"
# We might be just fine with the core here
RUN bash -c "eatmydata apt-get install -y -q fsl-core fsl-first-data"

RUN apt-get clean

# Setting up conda environment given simple_workflow specifications
WORKDIR /opt/repronim/simple_workflow
RUN curl -Ok https://raw.githubusercontent.com/ReproNim/simple_workflow/e4063fa95cb494da496565ec27c4ffe8a4901c45/Simple_Prep.sh
# conda installations take way too long -- might benefit from setting up
# to use proxy
# http://stackoverflow.com/a/31120854
RUN bash Simple_Prep.sh

#
# There seems to be no easy consistent way to load our customizations to env
# variables for both interactive and non-interactive shells. So let's create
# a file which would have all the necessary tuneups which would be passed
# explicitly into bash
#
RUN bash -c 'echo -e "echo IN setup_environments\n. /etc/fsl/fsl.sh\nexport PATH=/root/miniconda2/bin:\$PATH\nsource activate bh_demo\n" > setup_environment'

# Make fsl available in the containers by pointing ENV variable to it
# which both bash and dash (ubuntu) should warrant
# ENV ENV /etc/fsl/fsl.sh
# not effective :-/ for now let's try to place in bashrc
# RUN bash -c "echo '. /etc/fsl/fsl.sh' >> /etc/bash.bashrc"

# Tune the environment variables
#ENV PATH /root/miniconda2/bin:$PATH
# RUN bash -c "echo 'source activate bh_demo' >> /etc/bash.bashrc"

# Tune bash behavior so it loads our environment setup even in non-interactive mode
ENV ENV /opt/repronim/simple_workflow/setup_environment
RUN bash -c 'echo -e ". /opt/repronim/simple_workflow/setup_environment" >> /etc/profile'

# Let's setup user matching user
## RUN groupadd --gid 47522 -r yoh && useradd -m --uid 47521 -g yoh yoh

## CMD ["/bin/bash"]
