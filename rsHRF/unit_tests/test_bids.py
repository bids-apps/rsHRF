import io
import json
import contextlib

import pytest

from rsHRF.utils import bids

ENV_KEYS = [
    "RSHRF_DOCKER_TAG",
    "RSHRF_SINGULARITY_URL",
    "FMRIPREP_DOCKER_TAG",
    "FMRIPREP_SINGULARITY_URL",
]


@pytest.fixture
def clean_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _write(tmp_path):
    src = tmp_path / "src"
    deriv = tmp_path / "deriv"
    src.mkdir()
    deriv.mkdir()
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        bids.write_derivative_description(src, deriv)
    desc = json.loads((deriv / "dataset_description.json").read_text())
    return desc, stdout.getvalue()


def test_docker_tag_reads_its_own_env_var(clean_env, monkeypatch, tmp_path):
    """Guard checks RSHRF_DOCKER_TAG, so the body must read it too (was KeyError)."""
    monkeypatch.setenv("RSHRF_DOCKER_TAG", "1.7.0")
    desc, _ = _write(tmp_path)
    container = desc["GeneratedBy"][0]["Container"]
    assert container["Type"] == "docker"
    assert container["Tag"] == "bids/rshrf:1.7.0"


def test_singularity_uri_is_never_null(clean_env, monkeypatch, tmp_path):
    """The singularity branch used to getenv() a variable it never gated on."""
    monkeypatch.setenv("RSHRF_SINGULARITY_URL", "shub://BIDS-Apps/rsHRF")
    desc, _ = _write(tmp_path)
    container = desc["GeneratedBy"][0]["Container"]
    assert container["Type"] == "singularity"
    assert container["URI"] == "shub://BIDS-Apps/rsHRF"


def test_no_container_key_without_env(clean_env, tmp_path):
    desc, _ = _write(tmp_path)
    assert "Container" not in desc["GeneratedBy"][0]


def test_writes_no_stdout(clean_env, tmp_path):
    """A library function must not print; it used to emit the version string."""
    _, stdout = _write(tmp_path)
    assert stdout == ""


def test_dataset_type_is_the_bids_key(clean_env, tmp_path):
    desc, _ = _write(tmp_path)
    assert desc["DatasetType"] == "derivative"
