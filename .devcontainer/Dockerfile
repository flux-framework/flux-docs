FROM fluxrm/flux-sched:focal

LABEL maintainer="Vanessasaurus <@vsoch>"

# Pip not provided in this version
USER root
RUN apt-get update && apt-get install -y python3-venv
COPY ./requirements.txt /requirements.txt
COPY ./.github/dev-requirements.txt /dev-requirements.txt

ENV PYTHONPATH=/usr/lib/flux/python3.8

# For easier Python development.
RUN python3 -m pip install IPython && \
    python3 -m pip install -r /requirements.txt && \
    python3 -m pip install -r /dev-requirements.txt

ENV PATH=/env/bin:${PATH}
