######################################################
# Generate a Dockerfile and Singularity recipe for building a rshrf container
# (http://bids-apps.neuroimaging.io/rsHRF/).
# The Dockerfile and/or Singularity recipe installs most of rshrf's dependencies.
#
# Steps to build, upload, and deploy the rshrf docker and/or singularity image:
#
# 1. Create or update the Dockerfile and Singuarity recipe:
# bash generate_rshrf_images.sh
#
# 2. Build the docker image:
# docker build -t rshrf -f Dockerfile .
# OR
# bash generate_rshrf_images.sh docker
#
#    and/or singularity image:
# singularity build mindboggle.simg Singularity
# OR
# bash generate_rshrf_images.sh singularity
#
#   and/or both:
# bash generate_rshrf_images.sh both
#
# 3. Push to Docker hub:
# (https://docs.docker.com/docker-cloud/builds/push-images/)
# export DOCKER_ID_USER="your_docker_id"
# docker login
# docker tag rshrf your_docker_id/rshrf:tag  # See: https://docs.docker.com/engine/reference/commandline/tag/
# docker push your_docker_id/rshrf:tag
#
# 4. Pull from Docker hub (or use the original):
# docker pull your_docker_id/rshrf
#
# In the following, the Docker container can be the original (rshrf)
# or the pulled version (ypur_docker_id/rshrf:tag), and is given access to /Users/rshrf
# on the host machine.
#
# 5. Enter the bash shell of the Docker container, and add port mappings:
# docker run --rm -ti -v /Users/rshrf:/home/rshrf -p 8888:8888 -p 5000:5000 your_docker_id/rshrf
#
#
###############################################################################

image="kaczmarj/neurodocker:0.6.0"

set -e

generate_docker() {
 docker run --rm ${image} generate docker \
            --base neurodebian \
            --pkg-manager apt \
            --install libpng freetype libstdc++ openblas libxml2 libxslt g++ gfortran file binutils \
                      openblas-dev python3-dev gcc build-base libpng-dev musl-dev freetype-dev libxml2-dev libxslt-dev \
            --user=rshrf \
            --miniconda \
               conda_install="python=3.7 pandas scipy==1.3.3 numpy matplotlib joblib" \
               pip_install='rsHRF' \
               create_env='rshrf' \
               activate=true \
            --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
            --entrypoint="/neurodocker/startup.sh" \
            --workdir "/home/rshrf" \
            --cmd rshrf
}

generate_singularity() {
  docker run --rm ${image} generate singularity \
            --base neurodebian \
            --pkg-manager apt \
            --install libpng freetype libstdc++ openblas libxml2 libxslt g++ gfortran file binutils \
                      openblas-dev python3-dev gcc build-base libpng-dev musl-dev freetype-dev libxml2-dev libxslt-dev \
            --user=rshrf \
            --miniconda \
               conda_install="python=3.7 pandas scipy==1.3.3 numpy matplotlib joblib" \
               pip_install='rsHRF' \
               create_env='rshrf' \
               activate=true \
            --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
            --entrypoint="/neurodocker/startup.sh" \
            --workdir "/home/rshrf" 
 }

# generate files
generate_docker > Dockerfile
generate_singularity > Singularity

# check if images should be build locally or not
if [ '$1' = 'docker' ]; then
 echo "docker image will be build locally"
 # build image using the saved files
 docker build -t rshrf .
elif [ '$1' = 'singularity' ]; then
 echo "singularity image will be build locally"
 # build image using the saved files
 singularity build rshrf.simg Singularity
elif [ '$1' = 'both' ]; then
 echo "docker and singularity images will be build locally"
 # build images using the saved files
 docker build -t rshrf .
 singularity build rshrf.simg Singularity
else
echo "Image(s) won't be build locally."
fi
