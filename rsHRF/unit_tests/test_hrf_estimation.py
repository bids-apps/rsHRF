import pytest
import numpy as np
from rsHRF.utils import hrf_estimation

_SIG = np.array(
    [
        9.0,
        8.5,
        9.2,
        8.8,
        9.1,
        1.0,
        2.2,
        1.1,
        3.4,
        1.2,
        2.0,
        3.6,
        1.5,
        1.3,
        3.2,
        1.4,
        2.8,
        1.6,
        2.1,
        1.7,
    ]
)
_MASK = [0] * 5 + [1] * 15


def test_apply_localK_default():
    """
    Tests hrf_estimation.apply_localK_default() function.
    If localK is not entered by the user and TR <= 2, then localK is fixed to 1
    Else localK is fixed to 2.
    If localK is entered by the user it is fixed to user's input.
    """
    para = {
        "TR": 2.0,
        "localK": None,
    }
    hrf_estimation.apply_localK_default(para)
    assert (
        para["localK"] == 1
    ), f'Test failed for TR:{para["TR"]} the returned localK is: {para["localK"]}'

    para = {
        "TR": 3.0,
        "localK": None,
    }
    hrf_estimation.apply_localK_default(para)
    assert (
        para["localK"] == 2
    ), f'Test failed for TR:{para["TR"]} the returned localK is: {para["localK"]}'

    para = {
        "TR": 3.0,
        "localK": 5,
    }
    hrf_estimation.apply_localK_default(para)
    assert (
        para["localK"] == 5
    ), f'Test failed for TR:{para["TR"]} the returned localK is: {para["localK"]}'

    para = {"TR": 2.0}
    hrf_estimation.apply_localK_default(para)
    assert (
        para["localK"] == 1
    ), f'Test failed for TR:{para["TR"]} the returned localK is: {para["localK"]}'


def test_event_vector_uses_only_kept_frames_for_scaling():
    """
    The mean and std that set the event threshold must come from the kept frames
    only. If the dropped frames leak in through index 0, the scale either inflates and no
    peak clears the threshold or deflates and non-peak signals are interpreted as peaks.
    The signal here has five motion-corrupted frames at
    the start (approx. 9) that the mask drops, and three clear peaks in the rest (approx. 2).
    """
    tm = [0] * 5 + [1] * 15
    N = len(_SIG)
    expected = [8, 11, 14]

    events = hrf_estimation.wgr_BOLD_event_vector(N, _SIG, [1], 1, tm)
    events = events.toarray().ravel().nonzero()[0]
    masked_out = [i for i in events if tm[i] != 1]

    assert (
        list(events) == expected
    ), f"wrong events with a temporal mask. Expected: {expected}, got: {list(events)}"

    assert (
        not masked_out
    ), f"events were detected at frames the mask drops: {masked_out}"


def test_temporal_mask_is_not_modified():
    """
    compute_hrf sets para["temporal_mask] once and every voxel receives
    the same list, so the function must not write to it. Otherwise, the
    voxel converts the mask and every later voxel gets the converted version.
    """
    N = len(_SIG)
    tm = list(_MASK)
    tm_before = list(tm)
    hrf_estimation.wgr_BOLD_event_vector(N, _SIG, [1], 1, tm)

    assert (
        tm_before == tm
    ), f"The caller's temporal mask was modified: {tm_before} became {tm}"
