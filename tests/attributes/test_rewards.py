from dataclasses import fields

import pytest

from hunt.attributes.rewards import Rewards

_REWARD_FIELDS_COUNT: int = len(fields(Rewards))


@pytest.mark.parametrize("rewards, should_be_false", ((Rewards(*(1 for _ in range(_REWARD_FIELDS_COUNT))), False),
                                                      (Rewards(*(0 for _ in range(_REWARD_FIELDS_COUNT))), True)))
def test_rewards_implicit_bool_cast(rewards: Rewards, should_be_false: bool) -> None:
    """
    Test Rewards.__bool__ by generating Rewards instances and check for truthiness.
    """
    if not should_be_false:
        assert bool(rewards)
    else:
        assert not bool(rewards)
