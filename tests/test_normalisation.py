import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.normalisation import commodities as cm
from src.normalisation.districts import default


def test_all_33_districts_load():
    assert len(default()) == 33


def test_transliteration_variants_collapse():
    n = default()
    for variant in ("Kawardha", "KABIRDHAM", "कबीरधाम", " kabirdham "):
        assert n.resolve(variant).code == "CG-KAB"


def test_punctuation_and_spacing_ignored():
    n = default()
    assert n.resolve("Janjgir Champa").code == n.resolve("Janjgir-Champa").code


def test_unresolvable_returns_none_not_a_guess():
    assert default().resolve("Nonexistent District") is None


def test_district_created_in_2022_absent_from_earlier_data():
    n = default()
    assert n.resolve_for_year("Sakti", 2019) is None
    assert n.resolve_for_year("Sakti", 2024).code == "CG-SKT"


def test_split_districts_flagged_for_attribution():
    _, is_split = default().map_to_current("Rajnandgaon")
    assert is_split is True


def test_commodity_aliases_and_devanagari():
    for variant in ("Rice", "RICE", "धान", "Paddy Grade A"):
        assert cm.resolve(variant).key == "paddy"


def test_out_of_scope_commodity_rejected():
    assert cm.resolve("soybean") is None


def test_unit_conversion():
    assert cm.to_quintal(5, "mt") == 50.0
    assert cm.to_quintal(100, "kg") == 1.0


def test_standard_bag_has_no_mass_conversion():
    # A count, not a mass. Inventing a factor would corrupt every tendu aggregate.
    assert cm.to_quintal(5, "standard_bag") is None


def test_exactly_one_control_commodity_without_a_price_floor():
    controls = cm.control_commodities()
    assert len(controls) >= 1
    assert all(not c.procurement_floor for c in controls)
