# This a development container for VSCode
# To create a production container, I recommend this article:
# https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
# Use an NVIDIA CUDA base image
FROM nvidia/cuda:12.3.1-devel-ubuntu22.04

ARG USERNAME=navid
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages (using Python 3.10)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-distutils \
    python3.10-dev \
    build-essential \
    curl \
    git \
    openssh-client \
    iproute2 \
    procps \
    lsb-release \
    sudo \
    wget \
    tree \
    graphviz \
    graphviz-dev \
    libgraphviz-dev \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && update-alternatives --set python3 /usr/bin/python3.10 \
    && ln -s /usr/bin/python3 /usr/bin/python

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -m -s /bin/bash --uid $USER_UID --gid $USER_GID $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
    
USER $USERNAME
WORKDIR /home/$USERNAME

# Install pip and poetry
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 \
    && python3.10 -m pip install --user poetry==1.7.0

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Copy project files
COPY --chown=$USER_UID:$USER_GID pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi
