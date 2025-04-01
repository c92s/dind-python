import time
import pytest
import docker
import requests
import os

IMAGE_TAG = "dind-python:latest"


@pytest.fixture(autouse=True)
def teardown():
    client = docker.from_env()
    yield
    for c in client.containers.list(all=True):
        c.stop()
        c.remove(force=True)

    for i in client.images.list():
        client.images.remove(i.id, force=True)


@pytest.fixture
def image():
    return docker.from_env().images.build(path=".", tag=IMAGE_TAG)[0]


def test_docker_build(image):
    assert image.tags[0] == IMAGE_TAG
    assert image.attrs["RepoTags"][0] == IMAGE_TAG


def test_docker_use_image_as_base(image):
    os.makedirs("build", exist_ok=True)
    with open("build/dockerfile", "w") as f:
        f.write(f"""
FROM {IMAGE_TAG}
ENTRYPOINT ["python3", "-m", "http.server", "1234"]
""")

    # build the new image
    image, _ = docker.from_env().images.build(
        path="build/", tag="new-image:latest", dockerfile="dockerfile"
    )

    assert image.tags[0] == "new-image:latest"
    assert image.attrs["RepoTags"][0] == "new-image:latest"

    # run the new image
    container = docker.from_env().containers.run(
        "new-image:latest", detach=True, ports={"1234/tcp": 1234}
    )

    time.sleep(1)  # wait for the server to start
    assert container.attrs["Config"]["ExposedPorts"].get("1234/tcp") is not None
    assert requests.get("http://localhost:1234").status_code == 200

    # cleanup
    container.stop()
    container.remove(force=True)
    image.remove(force=True)
