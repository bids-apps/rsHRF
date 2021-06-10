import pytest
import numpy as np
from rsHRF.processing import knee 

def test_knee_pt():
    size = np.random.randint(10, 100)
    y = np.random.random(size) + np.random.random(size) * 1j
    out1, out2 = knee.knee_pt(y)
    assert type(out1) == np.int_
    assert type(out2) == np.int_
    y = np.zeros(size) + np.zeros(size) * 1j
    out1, out2 = knee.knee_pt(y)
    assert out1 == 2
    assert out2 == 1
    y = np.ones(size) + np.ones(size) * 1j
    out1, out2 = knee.knee_pt(y)
    assert out1 == 2
    assert out2 == 1
    y = np.asarray([(0.13638490363348788+0.4483173781686369j), (0.21565052592551615+0.5219779191597427j), (0.9979379796276104+0.07548834892584189j), (0.29470166952920507+0.36391228981190515j), (0.3464996550382653+0.0014059490581040945j), (0.4641546533051284+0.06567864084007502j), (0.46315096641592435+0.3323511950388086j), (0.17130338335642903+0.9791635674939458j), (0.9625869976661646+0.5830153856154539j), (0.8588617152267485+0.6576125931014645j)])
    out1, out2 = knee.knee_pt(y)
    assert out1 == 6
    assert out2 == 5