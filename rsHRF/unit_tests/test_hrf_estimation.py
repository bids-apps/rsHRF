import pytest
from rsHRF.utils import hrf_estimation


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
