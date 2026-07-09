from typing import Any

import sys
import pytest
from unittest import mock
from .. import CLI
import numpy as np
import nibabel as nib
from ..utils.default_parameters import default_parameters
import pandas as pd
import json
from pathlib import Path

SHAPE = (10, 10, 10, 10)
mockTR = 2


def get_data(image_type, TR=mockTR):
    data = np.zeros(SHAPE, dtype=np.int16)

    if image_type == "nifti":
        data = nib.Nifti1Image(data, np.eye(4))
        hdr = data.header
        hdr.set_zooms(TR * np.ones(len(SHAPE)))
        data = nib.Nifti1Image(data, np.eye(4), hdr)
    else:
        data = nib.gifti.GiftiDataArray(data.astype(np.float32), datatype="float32")
    return data


def fake_BIDS_dataset(
    path: Path,
    participants: list[str],
    description: dict[str, str],
    inner_files: dict[str, str],
) -> Path:
    root = path / "dsFAKE_BIDS"
    root.mkdir()
    partic = pd.DataFrame(
        {
            "participant_id": participants,
            "sex": [
                "F",
            ]
            * len(participants),
            "age": [
                10,
            ]
            * len(participants),
        }
    )
    partic.to_csv(root / "participants.tsv", sep="\t")
    descri = {
        "BIDSVersion": "1.0.0",
        "License": " ",
        "Name": "rest",
        "ReferencesAndLinks": ["References", "Links"],
    }
    df = root / "dataset_description.json"
    df.write_text(json.dumps(descri, indent=1))
    der = root / "derivatives"
    der.mkdir()
    rshrf = der / "rsHRF"
    rshrf.mkdir()
    fmrip = der / "fmriprep"
    fmrip.mkdir()
    descri.update(description)
    df = fmrip / "dataset_description.json"
    df.write_text(json.dumps(descri, indent=1))
    for subject in participants:
        sf = fmrip / f"sub-{subject}"
        sf.mkdir()
        func = sf / "func"
        func.mkdir()
        for file in inner_files:
            fil = func / file.format(subject)
            fil.write_text(inner_files[file])
    return root


def test_GUI(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["rsHRF", "GUI", "--no-bids"])
    with mock.patch("rsHRF.rsHRF_GUI.run.run") as mock_call:
        CLI.run_rsHRF()
        mock_call.assert_called_once()


def test_text(monkeypatch, tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("mock", encoding="utf-8")
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys, "argv", ["rsHRF", p._str, d._str, "--no-bids", "--TR", "2"]
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()

    monkeypatch.setattr(sys, "argv", ["rsHRF", p._str, d._str, "--TR", "2"])
    with pytest.raises(SystemExit):
        CLI.run_rsHRF()

    monkeypatch.setattr(sys, "argv", ["rsHRF", p._str, d._str, "--no-bids"])
    with pytest.raises(SystemExit):
        CLI.run_rsHRF()

    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        with pytest.warns(Warning):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    p._str,
                    d._str,
                    "--no-bids",
                    "--TR",
                    "2",
                    "--participant-label",
                    "001",
                ],
            )
            CLI.run_rsHRF()
        mock_call.assert_called_once()


def test_temporal_mask(monkeypatch, tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("mock", encoding="utf-8")
    m = d / "mask.txt"
    m.write_text("01011100", encoding="utf-8")
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                p._str,
                d._str,
                "--no-bids",
                "--TR",
                "2",
                "--temporal-mask",
                m._str,
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()

    n = d / "mask2.txt"
    n.write_bytes(np.arange(5, dtype=float).tobytes())
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                p._str,
                d._str,
                "--no-bids",
                "--TR",
                "2",
                "--temporal-mask",
                n._str,
            ],
        )
        CLI.run_rsHRF()


def test_bad_paths(monkeypatch, tmp_path):
    di = tmp_path / "inp"
    di.mkdir()
    p = di / "hello.txt"
    p.write_text("mock", encoding="utf-8")
    do = tmp_path / "outp"
    do.mkdir()

    cli_inputs = [
        ["rsHRF", di._str, do._str],  # assumes BIDS input but "participant" is missing
        [
            "rsHRF",
            p._str,
            "--no-bids",
            "--TR",
            "2",
        ],  # assumes text but no output directory
        [
            "rsHRF",
            p._str,
            str(tmp_path / "fake"),
            "--no-bids",
            "--TR",
            "2",
        ],  # assumes text but missing output directory
        [
            "rsHRF",
            str(di / "fake.txt"),
            do._str,
            "--no-bids",
            "--TR",
            "2",
        ],  # assumes text but missing input file
    ]
    for cli_input in cli_inputs:
        monkeypatch.setattr(sys, "argv", cli_input)
        with pytest.raises(SystemExit):
            CLI.run_rsHRF()


def test_gnii(monkeypatch, tmp_path):
    test_file_1 = "test.gii"
    test_file_2 = "test.gii.gz"
    test_file_3 = "test.nii"
    test_file_4 = "test.nii.gz"
    test_files = [test_file_1, test_file_2, test_file_3, test_file_4]
    di = tmp_path / "inp"
    di.mkdir()
    with mock.patch("nibabel.load") as load_mock:
        for test_file in test_files:
            if "nii" in test_file:
                load_mock.return_value = get_data("nifti")
            elif "gii" in test_file:
                load_mock.return_value = get_data("gifti")
            p = di / test_file
            p.write_text("mock", encoding="utf-8")

            monkeypatch.setattr(
                sys,
                "argv",
                ["rsHRF", p._str, di._str, "--no-bids"]
                + (["--TR", "2"] if "gii" in test_file else []),
            )
            with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
                CLI.run_rsHRF()
                para = {
                    k: default_parameters[k]
                    for k in [
                        "estimation",
                        "passband",
                        "passband_deconvolve",
                        "T",
                        "T0",
                        "TD_DD",
                        "AR_lag",
                        "thr",
                        "order",
                        "len",
                        "min_onset_search",
                        "max_onset_search",
                        "localK",
                        "wiener",
                    ]
                }
                para["temporal_mask"] = None
                para["TR"] = mockTR
                para["dt"] = para["TR"] / para["T"]
                para["lag"] = np.arange(
                    np.trunc(para["min_onset_search"] / para["dt"]),
                    np.trunc(para["max_onset_search"] / para["dt"]) + 1,
                    dtype="int",
                )
                mock_call.assert_called_once()

                call_args = mock_call.call_args
                print("call_args[0]", call_args[0])
                for good, mocked in zip(
                    [
                        p._str,
                        None,
                        di._str,
                        para,
                        -1,
                        test_file[4:],
                        "input",
                        [],
                        False,
                    ],
                    call_args[0],
                ):
                    print("good", good)
                    print("mocked", mocked)
                    if isinstance(good, dict):
                        good = {
                            k: v.tolist() if isinstance(v, np.ndarray) else v
                            for k, v in good.items()
                        }
                        mocked = {
                            k: v.tolist() if isinstance(v, np.ndarray) else v
                            for k, v in mocked.items()
                        }
                        assert good == mocked
                    else:
                        assert good == mocked


def test_gnii_bad_TR(monkeypatch, tmp_path):
    di = tmp_path / "inp"
    di.mkdir()
    with mock.patch("nibabel.load") as load_mock:
        load_mock.return_value = get_data("nifti", 0)
        p = di / "test.nii"
        p.write_text("mock", encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["rsHRF", p._str, di._str, "--no-bids"])
        with pytest.raises(SystemExit):
            CLI.run_rsHRF()

    with mock.patch("nibabel.load") as load_mock:
        load_mock.return_value = get_data("gifti")
        p = di / "test.gii"
        p.write_text("mock", encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["rsHRF", p._str, di._str, "--no-bids"])
        with pytest.raises(SystemExit):
            CLI.run_rsHRF()


def test_bad_masks(monkeypatch, tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("mock", encoding="utf-8")
    m = d / "mask.bad"
    m.write_text("bad", encoding="utf-8")
    with pytest.warns(Warning):
        with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
            monkeypatch.setattr(
                sys,
                "argv",
                ["rsHRF", p._str, d._str, "--no-bids", "--TR", "2", "-m", m._str],
            )
            CLI.run_rsHRF()
            mock_call.assert_called_once()

    with mock.patch("nibabel.load") as load_mock:
        load_mock.return_value = get_data("nifti")
        p = d / "test.nii"
        p.write_text("mock", encoding="utf-8")

        with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
            monkeypatch.setattr(
                sys, "argv", ["rsHRF", p._str, d._str, "--no-bids", "-m", "BIDS"]
            )
            with pytest.warns(Warning):
                CLI.run_rsHRF()
            mock_call.assert_called_once()

        with pytest.raises(SystemExit):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    p._str,
                    d._str,
                    "--no-bids",
                    "-m",
                    str(d / "fake.gii"),
                ],  # format mismatch
            )
            CLI.run_rsHRF()

        with pytest.raises(SystemExit):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    p._str,
                    d._str,
                    "--no-bids",
                    "-m",
                    str(d / "fake.nii"),
                ],  # missing file
            )
            CLI.run_rsHRF()

        with pytest.raises(SystemExit):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    p._str,
                    d._str,
                    "--no-bids",
                    "-m",
                    m._str,
                ],  # wrong extension
            )
            CLI.run_rsHRF()


def test_BIDS(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        with pytest.warns(Warning):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    str(ds / "derivatives" / "fmriprep"),
                    str(ds / "derivatives" / "rsHRF"),
                    "participant",
                    "--TR",
                    "2",
                ],
            )
            CLI.run_rsHRF()
            mock_call.assert_called_once()


def test_BIDS_failedComp(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    with mock.patch(
        "rsHRF.fourD_rsHRF.demo_rsHRF", side_effect=ValueError("mock error")
    ) as mock_call:
        with pytest.raises(RuntimeError):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    str(ds / "derivatives" / "fmriprep"),
                    str(ds / "derivatives" / "rsHRF"),
                    "participant",
                ],
            )
            CLI.run_rsHRF()
            mock_call.assert_called_once()
    with mock.patch(
        "rsHRF.fourD_rsHRF.demo_rsHRF", side_effect=KeyError("mock error")
    ) as mock_call:
        with pytest.raises(RuntimeError):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    str(ds / "derivatives" / "fmriprep"),
                    str(ds / "derivatives" / "rsHRF"),
                    "participant",
                ],
            )
            CLI.main()
            mock_call.assert_called_once()


def test_BIDS_TR(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest"}
            ),
        },
    )
    with mock.patch("nibabel.load") as load_mock:
        load_mock.return_value = get_data("nifti")
        with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    str(ds / "derivatives" / "fmriprep"),
                    str(ds / "derivatives" / "rsHRF"),
                    "participant",
                ],
            )
            CLI.run_rsHRF()
            mock_call.assert_called_once()


def test_BIDS_nonDerivative(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "original"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
            ],
        )
        CLI.run_rsHRF()


def test_BIDS_noDerivativeInfo(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
            ],
        )
        CLI.run_rsHRF()


def test_BIDS_noDatasetDescription(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    (ds / "derivatives" / "fmriprep" / "dataset_description.json").unlink()
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
            ],
        )
        CLI.run_rsHRF()


def test_BIDS_participantLabels(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
        },
    )
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "--participant-label",
                "01",
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "--participant-label",
                "02",
            ],
        )
        CLI.run_rsHRF()


def test_BIDS_mask(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz": "fake",
        },
    )
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "-m",
                "BIDS",
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()

    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "-m",
                str(
                    ds
                    / "derivatives"
                    / "fmriprep"
                    / "sub-01"
                    / "func"
                    / "sub-01_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"
                ),
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()


def test_BIDS_mask_bad(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.gii.gz": "fake",
        },
    )
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "-m",
                "BIDS",
            ],
        )
        CLI.run_rsHRF()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "-m",
                str(
                    ds
                    / "derivatives"
                    / "fmriprep"
                    / "sub-01"
                    / "func"
                    / "sub-01_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"
                ),
            ],
        )
        CLI.run_rsHRF()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "-m",
                str(
                    ds
                    / "derivatives"
                    / "fmriprep"
                    / "sub-01"
                    / "func"
                    / "sub-01_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.gii.gz"
                ),
            ],
        )
        CLI.run_rsHRF()


def test_BIDS_filters(monkeypatch, tmp_path):
    ds = fake_BIDS_dataset(
        tmp_path,
        ["01"],
        {"DataType": "derivative"},
        {
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz": "fake",
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json": json.dumps(
                {"TaskName": "Rest", "RepetitionTime": 2}
            ),
            "sub-{}_task-rest_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz": "fake",
        },
    )
    filter = ds / "filter.json"
    filter.write_text(json.dumps({"bold": {}, "mask": {}}))
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "--bids-filter-file",
                filter._str,
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()

    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(ds / "derivatives" / "fmriprep"),
                str(ds / "derivatives" / "rsHRF"),
                "participant",
                "--bids-filter-file",
                filter._str,
                "-m",
                "BIDS",
            ],
        )
        CLI.run_rsHRF()
        mock_call.assert_called_once()


def test_temporal_mask_rejects_non_binary_tokens(monkeypatch, tmp_path):
    """A text file with a stray non-0/1 token was silently absorbed into a wrong mask."""
    d = tmp_path / "sub"
    d.mkdir()
    (d / "hello.txt").write_text("mock", encoding="utf-8")
    bad = d / "mask.txt"
    bad.write_text("0 1 2 1", encoding="utf-8")  # the '2' used to vanish -> [0, 1, 1]
    with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF"):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rsHRF",
                str(d / "hello.txt"),
                str(d),
                "--no-bids",
                "--TR",
                "2",
                "--temporal-mask",
                str(bad),
            ],
        )
        with pytest.raises(SystemExit):
            CLI.run_rsHRF()


def test_temporal_mask_accepts_valid_formats(monkeypatch, tmp_path):
    """A concatenated row and separator-delimited files must both still parse."""
    d = tmp_path / "sub"
    d.mkdir()
    (d / "hello.txt").write_text("mock", encoding="utf-8")
    for content in ("01011100", "0 1 0 1 1 1 0 0", "0,1,0,1"):
        m = d / "mask.txt"
        m.write_text(content, encoding="utf-8")
        with mock.patch("rsHRF.fourD_rsHRF.demo_rsHRF") as mock_call:
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "rsHRF",
                    str(d / "hello.txt"),
                    str(d),
                    "--no-bids",
                    "--TR",
                    "2",
                    "--temporal-mask",
                    str(m),
                ],
            )
            CLI.run_rsHRF()
            mock_call.assert_called_once()
