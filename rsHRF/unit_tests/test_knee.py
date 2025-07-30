import pytest
import numpy as np
from ..processing import knee 

def test_knee_pt():
    size = np.random.randint(10, 99)
    y = np.random.random(size) + np.random.random(size) * 1j
    out1, out2 = knee.knee_pt(y)
    assert isinstance(out1, (int, np.integer)), f"Expected integer type, got {type(out1)}"
    assert isinstance(out2, (int, np.integer)), f"Expected integer type, got {type(out2)}"
    y = np.zeros(size) + np.zeros(size) * 1j
    out1, out2 = knee.knee_pt(y)
    assert out1 == 2
    assert out2 == 1
    y = np.asarray([(0.13638490363348788+0.4483173781686369j), (0.21565052592551615+0.5219779191597427j), (0.9979379796276104+0.07548834892584189j), (0.29470166952920507+0.36391228981190515j), (0.3464996550382653+0.0014059490581040945j), (0.4641546533051284+0.06567864084007502j), (0.46315096641592435+0.3323511950388086j), (0.17130338335642903+0.9791635674939458j), (0.9625869976661646+0.5830153856154539j), (0.8588617152267485+0.6576125931014645j)])
    out1, out2 = knee.knee_pt(y)
    assert out1 == 6
    assert out2 == 0