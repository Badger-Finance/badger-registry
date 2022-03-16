import brownie
from brownie import ZERO_ADDRESS


def test_set_gov(registry, gov, alt_gov, rando):
    with brownie.reverts():
        registry.setGovernance(rando, {"from": rando})

    registry.setGovernance(alt_gov, {"from": gov})
    assert registry.governance() == alt_gov

    with brownie.reverts():
        registry.setGovernance(gov, {"from": gov})


def test_set_dev(registry, gov, alt_gov, dev, rando):
    with brownie.reverts():
        registry.setDev(rando, {"from": rando})

    registry.setDev(alt_gov, {"from": gov})
    assert registry.devGovernance() == alt_gov

    with brownie.reverts():
        registry.setDev(dev, {"from": dev})

    registry.setDev(dev, {"from": alt_gov})
    assert registry.devGovernance() == dev


def test_set_strategist_guild(
    registry, gov, rando, strategist_guild, alt_strategist_guild
):
    threshold = 2

    with brownie.reverts():
        registry.setStrategistGuild([rando], threshold, {"from": rando})

    with brownie.reverts():
        registry.setStrategistGuild(alt_strategist_guild, 0, {"from": gov})

    with brownie.reverts():
        registry.setStrategistGuild([ZERO_ADDRESS], 1, {"from": gov})

    registry.setStrategistGuild(alt_strategist_guild, threshold, {"from": gov})
    for i in range(len(strategist_guild)):
        assert registry.isStrategist(strategist_guild[i]) == False
        assert registry.isStrategist(alt_strategist_guild[i]) == True
        assert registry.strategistGuild(i) == alt_strategist_guild[i]
    assert registry.multiSigThreshold() == threshold

    registry.setStrategistGuild([], threshold, {"from": gov})
    with brownie.reverts():
        registry.strategistGuild(i)
