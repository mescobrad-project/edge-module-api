FROM python:3.7-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/requirements.txt /usr/src/app/

RUN apt-get update && apt-get install -y git dcm2niix unzip gzip wget libgomp1

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src /usr/src/app

RUN wget -O /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/mri_deface \
  ftp://surfer.nmr.mgh.harvard.edu/pub/dist/mri_deface/mri_deface_linux && \
  chmod +x /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/mri_deface

RUN wget -O /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/face.gca.gz \
  ftp://surfer.nmr.mgh.harvard.edu/pub/dist/mri_deface/face.gca.gz && \
  gunzip /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/face.gca.gz

RUN wget -O /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/talairach_mixed_with_skull.gca.gz \
  ftp://surfer.nmr.mgh.harvard.edu/pub/dist/mri_deface/talairach_mixed_with_skull.gca.gz && \
  gunzip /usr/src/app/mescobrad_edge/plugins/mri_anonymisation_plugin/deface_files/talairach_mixed_with_skull.gca.gz

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "mescobrad_edge"]