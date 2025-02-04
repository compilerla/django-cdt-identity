import logging

logger = logging.getLogger(__name__)


class Claims:

    def __init__(self, userinfo: dict, expected_claims: list[str]):
        """Process expected claims from the userinfo dict.

        - Boolean claims look like `{ "claim": "1" | "0" }` or `{ "claim": "true" }`
        - Value claims look like `{ "claim": "value" }`
        """
        self.claims = {}
        self.errors = {}

        for claim in expected_claims:
            claim_value = userinfo.get(claim)
            if not claim_value:
                logger.warning(f"userinfo did not contain claim: {claim}")
            try:
                claim_value = int(claim_value)
            except (TypeError, ValueError):
                pass
            if isinstance(claim_value, int):
                if claim_value == 1:
                    # a value of 1 means True
                    self.claims[claim] = True
                elif claim_value >= 10:
                    # values greater than 10 indicate an error condition
                    self.errors[claim] = claim_value
            elif isinstance(claim_value, str):
                if claim_value.lower() == "true":
                    # any form of the value "true" means True
                    self.claims[claim] = True
                elif claim_value.lower() != "false":
                    # if userinfo contains claim and the value is not "false", store the value
                    self.claims[claim] = claim_value

    def __contains__(self, claim: str):
        """Check if a claim is in the processed claims."""
        return claim in self.claims

    def __getitem__(self, claim: str):
        """Allow dictionary-style access to claims."""
        return self.claims[claim]

    def get(self, claim: str, default=None):
        """Return the value for claim if the claim was processed, else default."""
        return self.claims.get(claim, default)
