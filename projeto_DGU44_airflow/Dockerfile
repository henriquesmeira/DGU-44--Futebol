FROM apache/airflow:2.8.1

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER root
RUN groupadd -g 50000 airflow || true # Adiciona o grupo se não existir
RUN chown -R airflow:airflow /opt/airflow

USER airflow