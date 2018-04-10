from models.variant import Variant


def test_variant_tags():
    v = Variant()
    v.variant_tags = {'aga', 'whdload'}
    assert 'AGA' in v.variant_display_tags
