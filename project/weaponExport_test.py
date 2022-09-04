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
    # missile cost
    ('MISSILES_FREE', '1'),
    ('MISSILES_1', '1/1{{Missile}}'),
    ('SLOTGUN_CHAOS', '12/3{{Missile}}'),
    # projectile count
    ('RUSTY_MISSILES_BURST', '2/1{{Missile}}'),
    ('SHOTGUN_1', '2'),
    ('SHOTGUN_2', '3'),
    ('CLONE_CANNON_BABYORCHID', '20'),
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
])

def testGetPierce(blueprintName, expected):
    blueprintPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
    blueprint = blueprintUtils.getNormalBlueprint(blueprintPath)
    weapon = Weapon(blueprint)
    assert weapon.getPierce() == expected
