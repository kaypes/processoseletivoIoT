# Use the official ESP-IDF image
FROM espressif/idf:v5.2.2

# Set ESP-IDF path
ENV IDF_PATH="/opt/esp/idf/"

WORKDIR "/"

# RUN mkdir -p /fs
COPY src/main.py /main.py
# COPY boot.py /boot.py
COPY src/config.py /config.py
COPY src/morse_dict.py /morse_dict.py
COPY src/hal.py /hal.py
COPY src/input_handler.py /input_handler.py
COPY src/display_driver.py /display_driver.py
COPY src/fsm.py /fsm.py
COPY src/ssd1306.py /ssd1306.py
COPY src/async_queue.py /async_queue.py

RUN git clone https://github.com/earlephilhower/mklittlefs.git && \
  cd mklittlefs && \
  git submodule update --init && \
  make dist && \
  ./mklittlefs --version

RUN cd mklittlefs && \
  mkdir -p ~/fs && \
  cp /main.py ~/fs/main.py && \
  #  cp /boot.py ~/fs/boot.py && \
  cp /config.py ~/fs/config.py && \
  cp /morse_dict.py ~/fs/morse_dict.py && \
  cp /hal.py ~/fs/hal.py && \
  cp /input_handler.py ~/fs/input_handler.py && \
  cp /display_driver.py ~/fs/display_driver.py && \
  cp /fsm.py ~/fs/fsm.py && \
  cp /ssd1306.py ~/fs/ssd1306.py && \
  cp /async_queue.py ~/fs/async_queue.py && \
  ./mklittlefs -c ~/fs -b 4096 -p 256 -s 0x200000 /fs.bin


CMD ["/bin/bash"]
