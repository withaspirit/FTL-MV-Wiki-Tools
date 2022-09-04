# to use this do 'python -m pip install pytest' in cmd
# run command:  pytest project/
import pytest
import xml.etree.ElementTree
import blueprintUtils
from weaponExport import Weapon

# https://realpython.com/python-testing/#automated-vs-manual-testing
# https://realpython.com/pytest-python-testing/#marks-categorizing-tests

@pytest.mark.parametrize('blueprintName, expected', [
    ('BEAM_1', ''),
    ('LASER_BURST_2', '2'),
    # projectile count
    ('RUSTY_MISSILES_BURST', '2/1{{Missile}}'),
    ('SHOTGUN_1', '2'),
    ('SHOTGUN_2', '3'),
    ('CLONE_CANNON_BABYORCHID', '20'),
     # missile cost
    ('MISSILES_FREE', '1'),
    ('MISSILES_1', '1/1{{Missile}}'),
    ('SLOTGUN_CHAOS', '12/3{{Missile}}'),
    # chargeLevels
    ('LASER_CHARGEGUN', '1-2'),
    ('SHOTGUN_CHARGE', '1-3'),
    ('MISSILES_BURST', '1-3/1{{Missile}}'),
    # ammo chance (TODO)
    ('KERNEL_1', '2/1{{Missile}}'),
    # accuracy
    ('BOMB_1', '1/1{{Missile}} {{Accuracy|30}}'),
    ('LOOT_MATH_2', '1/2{{Missile}} {{Accuracy|30}}'),
])
def testGetShots(blueprintName, expected):
    blueprintPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
    blueprint = blueprintUtils.getNormalBlueprint(blueprintPath)
    weapon = Weapon(blueprint)
    assert weapon.getShots() == expected

@pytest.mark.parametrize('blueprintName, expected', [
    # regular pierce
    ('LASER_BURST_1', ''),
    ('LASER_PIERCE', '1'),
    ('MODULAR_ION_BASE_PIERCE', '3'),
    # beam piercing
    ('BEAM_2', ''),
    ('BIG_ION_CHAOS', '11'),
    ('BEAM_PIERCE', '2'),
    ('BEAM_FIRE_PIERCE', '3'),
    # missile pierce
    ('MISSILES_1', '10'),
    # gaster_blaster
    ('GASTER_BLASTER', '')
])
def testGetPierce(blueprintName, expected):
    blueprintPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
    blueprint = blueprintUtils.getNormalBlueprint(blueprintPath)
    weapon = Weapon(blueprint)
    assert weapon.getPierce() == expected

@pytest.mark.parametrize('blueprintName, expected', [
    ('LASER_BURST_1', ''),
    ('SHOTGUN_1', '42px'),
    ('RUSTY_LASER_BURST_2', '52px'),
    ('RUSTY_MISSILES_1', '52px')
])
def testGetRadius(blueprintName, expected):
    blueprintPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
    blueprint = blueprintUtils.getNormalBlueprint(blueprintPath)
    weapon = Weapon(blueprint)
    assert weapon.getRadius() == expected

@pytest.mark.parametrize('blueprintName, expected', [
    ('LASER_BURST_1', ''),
    ('BEAM_1', '45px')
])
def testGetLength(blueprintName, expected):
    blueprintPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
    blueprint = blueprintUtils.getNormalBlueprint(blueprintPath)
    weapon = Weapon(blueprint)
    assert weapon.getLength() == expected
