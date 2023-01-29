# Transferring the FUT Docker image to a new host

## Saving the Docker image

To save and compress a Docker image with the intent of using the image on
another host, use the following command once the desired image is already built:

```bash
DOCKER_IMAGE_NAME="fut-final:latest"
DOCKER_TARBALL_NAME="${DOCKER_IMAGE_NAME}-docker-$(date +%F).tar.gz"
docker save "${DOCKER_IMAGE_NAME}" | gzip -c > "${DOCKER_TARBALL_NAME}"
```

Alternatively, use the multiprocessing compression tool named `pigz`:

```bash
docker save "${DOCKER_IMAGE_NAME}" | pigz -c > "${DOCKER_TARBALL_NAME}"
```

## Saving the Docker image and build cache

Once the desired Docker image is built, use the following command to save and
compress the image together with its entire build cache:

```bash
docker save "${DOCKER_IMAGE_NAME}" $(docker history -q ${DOCKER_IMAGE_NAME}) | pigz -c > "${DOCKER_TARBALL_NAME}"
```

This enables you to use the Docker image, and to reuse the build cache which
speeds up image rebuilds on another host.

Note: Sometimes the `docker history` command produces the string `<missing>`
instead of the image ID. In this case, the above command will not work, and the
list of image names and IDs will need to be cleaned and provided to the
`docker save` command.

## Loading the Docker image

Once you have transferred the compressed Docker image to the desired host, for
example using `scp`, the image or images can be loaded into the new host.

Optionally, clear all existing Docker data if space on the host is low. Expect
upwards of `2GB to 3GB` to be needed for a successful import. This step is not
needed if enough disk space is available.

```bash
sudo docker system prune -a
```

To import the image or images, run the following command:

```bash
docker load -i "${DOCKER_TARBALL_NAME}"
```
