import rsHRF


def test_rsHRF_does_not_import_an_attribute_that_does_not_exist():
    missing_attr = [a for a in rsHRF.__all__ if not hasattr(rsHRF, a)]
    assert (
        len(missing_attr) == 0
    ), f"rsHRF does not have the following attributes:{missing_attr}"
