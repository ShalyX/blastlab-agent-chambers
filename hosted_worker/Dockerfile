FROM python:3.12-slim
WORKDIR /runtime
COPY worker.py blastlab_runtime.py /runtime/
RUN mkdir /agent && chmod 755 /agent
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
ENTRYPOINT ["python3", "-I", "-B", "-u", "/runtime/worker.py"]
