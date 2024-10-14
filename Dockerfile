FROM ubuntu:22.04

# define the folder where our src should exist/ be deposited
ARG BASE=/zk-comp
ARG SRC_SEAL=$BASE/python-seal
ARG SRC_CHARM=$BASE/charm-crypto
ARG SRC_OPENFHE=$BASE/openfhe-development
ARG SRC_OPENFHE_PY=$BASE/openfhe-python

RUN mkdir -p ${BASE} ${SRC_SEAL} ${SRC_CHARM} ${SRC_OPENFHE} ${SRC_OPENFHE_PY}

# prevents update and install asking for tz
ENV DEBIAN_FRONTEND=noninteractive

# Install common dependencies and create
# source / build directories
RUN apt update && \
    apt install -y git build-essential cmake python3 python3-dev python3-pip silversearcher-ag && \
    apt install -y bc



# Install Z3 for bit-expression
RUN pip3 install z3-solver
RUN pip3 install numpy "pybind11[global]"

WORKDIR ${BASE}
RUN git clone https://github.com/Huelse/SEAL-Python python-seal



# Setting our default directory to the one specified above
WORKDIR ${SRC_SEAL}

# Update submodules
RUN cd ${SRC_SEAL} && \
    git submodule update --init --recursive
    # git submodule update --remote

# Build and install seal + bindings
RUN cd ${SRC_SEAL}/SEAL && \
    cmake -S . -B build -DSEAL_USE_MSGSL=OFF -DSEAL_USE_ZLIB=OFF -DSEAL_USE_ZSTD=OFF && \
    cmake --build build && \
    cd ${SRC_SEAL} && \
    python3 setup.py build_ext -i

WORKDIR ${BASE}

RUN apt install -y clang

ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++

RUN git clone https://github.com/openfheorg/openfhe-development
RUN apt install -y libomp-dev
RUN cd ${SRC_OPENFHE} && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install

RUN pip3 install pytest
RUN git clone https://github.com/openfheorg/openfhe-python
RUN cd ${SRC_OPENFHE_PY} && \
    mkdir build && \
    cd build && \ 
    cmake .. && \
    make && \
    make install

# Install Charm-Crypto
# Credit: Charm-Crypto's Dockerfile ( https://github.com/JHUISI/charm )
RUN apt update && apt install --yes build-essential flex bison wget subversion m4 python3 python3-dev python3-setuptools libgmp-dev libssl-dev
RUN cd ${SRC_CHARM} && \
    git clone https://github.com/JHUISI/charm

RUN mkdir ${SRC_CHARM}/pbc-0.5.14

RUN cd ${SRC_CHARM} && \
    wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && \
    tar xvf pbc-0.5.14.tar.gz && \
    cd ./pbc-0.5.14 && ./configure LDFLAGS="-lgmp" && make && make install && ldconfig

RUN cd ${SRC_CHARM}/charm && ./configure.sh && make && make install && ldconfig

# Install Zama related stuff
RUN cd ${BASE} && \
    git clone https://github.com/zama-ai/concrete.git
RUN pip3 install concrete-python


# Install SymPy
pip3 install sympy

ENV PYTHONPATH=${SRC_CHARM}/build:${SRC_OPENFHE_PY}/build:${PYTHONPATH}

CMD ["/usr/bin/python3"]
