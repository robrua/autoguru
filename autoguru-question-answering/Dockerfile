FROM debian:stable-slim


ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8


# -- Install utilities
RUN apt-get update --fix-missing --no-install-recommends && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# -- Anaconda home setup
ENV CONDA_HOME /opt/conda
ENV PATH $CONDA_HOME/bin:$PATH


# -- Python version
ARG python_version=3.9


# -- Install Miniconda python
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/conda.sh && \
    /bin/bash ~/conda.sh -b -p $CONDA_HOME && \
    rm ~/conda.sh && \
    conda install -y python=${python_version} && \
    $CONDA_HOME/bin/conda clean -tipsy


# -- Install project dependencies
ADD requirements.txt /opt/autoguru/autoguru-question-answering/requirements.txt
RUN pip install -U --no-cache-dir -r /opt/autoguru/autoguru-question-answering/requirements.txt


# -- Install the project
ADD README.md /opt/autoguru/autoguru-question-answering/README.md
ADD MANIFEST.in /opt/autoguru/autoguru-question-answering/MANIFEST.in
ADD setup.py /opt/autoguru/autoguru-question-answering/setup.py
ADD setup.cfg /opt/autoguru/autoguru-question-answering/setup.cfg
ADD autoguru /opt/autoguru/autoguru-question-answering/autoguru/
RUN pip install -e /opt/autoguru/autoguru-question-answering/


# -- Launch project on run
ENTRYPOINT ["autoguru-qa"]