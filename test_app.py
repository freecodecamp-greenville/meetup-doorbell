from datetime import datetime

from utils import doorbell_is_active


def test_doorbell_is_active():
    # inactive before 6PM
    assert not doorbell_is_active(datetime(2018, 3, 1, 17, 59, 59))
    # active starting at 6PM
    assert doorbell_is_active(datetime(2018, 3, 1, 18, 0, 0))
    # active before 9PM
    assert doorbell_is_active(datetime(2018, 3, 1, 20, 59, 59))
    # inactive starting at 9PM
    assert not doorbell_is_active(datetime(2018, 3, 1, 21, 0, 0))
    # inactive on second thursday
    assert not doorbell_is_active(datetime(2018, 3, 8, 19, 0, 0))
    # inactive on third thursday
    assert not doorbell_is_active(datetime(2018, 3, 15, 19, 0, 0))
    # inactive on fourth thursday
    assert not doorbell_is_active(datetime(2018, 3, 22, 19, 0, 0))
    # inactive on fifth thursday
    assert not doorbell_is_active(datetime(2018, 3, 29, 19, 0, 0))
