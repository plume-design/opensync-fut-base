ARG PARENT_IMAGE=""
FROM $PARENT_IMAGE:latest

RUN pip3 install \
 google=="3.0.0" \
 pytest-cov=="3.0.0" \
 pytest-dependency=="0.5.1" \
 pytest-ordering=="0.6" \
 pytest-select=="0.1.2" \
 retry=="0.9.2 "
