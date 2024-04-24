FROM nvidia/cuda:11.3.1-devel-ubuntu20.04

RUN apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common -y && \
    add-apt-repository -y multiverse && apt-get update -y && apt-get upgrade -y && \
    apt-get install -y apt-utils nano vim man build-essential wget sudo && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install python3.8 python3-pip -y
RUN apt-get update -y && apt-get install -y curl libssl-dev openssl libopenblas-dev \
    libhdf5-dev hdf5-helpers hdf5-tools libhdf5-serial-dev libprotobuf-dev protobuf-compiler git

RUN pip install --upgrade pip && pip install marllib

RUN pip install protobuf==3.17 && pip install gym==0.20.0
