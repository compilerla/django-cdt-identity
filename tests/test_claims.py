import pytest

from cdt_identity.claims import Claims


@pytest.mark.parametrize(
    "userinfo, expected_claims, claims, errors",
    [
        # numeric flags
        (
            {"claim1": "1", "claim2": "0", "claim3": "15", "claim4": "-1"},
            ["claim1", "claim2", "claim3", "claim4"],
            {"claim1": True},
            {"claim3": 15},
        ),
        # boolean strings
        (
            {"claim1": "true", "claim2": "TRUE", "claim3": "false", "claim4": "FALSE"},
            ["claim1", "claim2", "claim3", "claim4"],
            {"claim1": True, "claim2": True},
            {},
        ),
        # string values
        (
            {"claim1": "not_a_number", "claim2": "$peci@l"},
            ["claim1", "claim2"],
            {"claim1": "not_a_number", "claim2": "$peci@l"},
            {},
        ),
        # missing values
        (
            {"claim1": "true", "claim3": "1"},
            ["claim1", "claim2"],
            {"claim1": True},
            {},
        ),
    ],
)
def test_claims(userinfo, expected_claims, claims, errors):
    obj = Claims(userinfo, expected_claims)

    assert obj.claims == claims
    assert obj.errors == errors

    for key, value in claims.items():
        assert obj[key] == value
        assert obj.get(key) == value
        assert key in obj
