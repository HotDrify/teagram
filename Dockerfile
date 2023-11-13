FROM python:3.10
ENV DOCKER=true
ENV GIT_PYTHON_REFRESH=quiet

ADD . /
RUN if [ "${DOCKERSYSTEM}" = "arch" ]; then \
        pacman -Syu --noconfirm && \
        pacman -S --noconfirm openssl git python python-pip; \
    elif [ "${DOCKERSYSTEM}" = "gentoo" ]; then \
        emerge --sync && \
        emerge --update --deep --with-bdeps=y && \
        emerge --ask --noreplace openssl git python pip; \
    elif [ "${DOCKERSYSTEM}" = "fedora" ]; then \
        dnf update -y && \
        dnf install -y openssl git python3 python3-pip; \
    else \
        apt update && \
        apt upgrade -y && \
        apt install -y openssl git python3 python3-pip; \
    fi

RUN pip install --no-warn-script-location -r requirements.txt
CMD python3.10 -m teagram   