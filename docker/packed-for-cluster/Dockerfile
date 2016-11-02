FROM senescence-in-field

RUN pip install pyyaml
RUN git clone https://github.com/JIC-Image-Analysis/senescence-in-field.git /code && \
cd /code && git checkout infrastructure-experiments && \
ln -s /code/scripts /scripts

ENV INCONTAINER=TRUE

ENTRYPOINT ["/scripts/agent.py"]
