FROM ubuntu:20.04 as build

WORKDIR /usr/src

# COPY --chown=root:root pip.conf /root/.config/pip/pip.conf

# -- Install Python3
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip

RUN python3 --version

# -- Install gstreamer core plugins, HW accelerators, libs & tools
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-doc \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-vaapi \
    python-gi \
    python-gi-cairo \
    gir1.2-gtk-3.0 \
    tzdata \
    dnsutils

# -- Copy source directories
COPY . /usr/src/

# -- Install dependencies
RUN pip3 install -r requirements.txt
# RUN pip3 install -r requirements.txt && rm /root/.config/pip/pip.conf

# -- Start the app
CMD ["python3", "src/main.py"]
