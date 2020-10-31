import os
from dataclasses import dataclass
from configparser import ConfigParser

import pyglet


@dataclass
class GameConfig:

    width: int = 250
    height: int = 500
    full_screen: bool = False

    def __init__(self, load_saved_config=True):
        module_name = __name__.split('.')[0]
        settings_path = pyglet.resource.get_settings_path(module_name)
        if not os.path.exists(settings_path):
            os.makedirs(settings_path)
        self.settings_file = os.path.join(settings_path, 'settings.cfg')
        if load_saved_config:
            self.load()

    def load(self):
        if not os.path.exists(self.settings_file):
            return
        config = ConfigParser()
        config.read(self.settings_file)
        self._parse_config(config)

    def _parse_config(self, config):
        settings_config = config['Settings']
        for field in self.__dataclass_fields__.values():
            if field.name in settings_config:
                if field.type == bool:
                    val = settings_config.getboolean(field.name)
                elif field.type == int:
                    val = settings_config.getint(field.name)
                elif field.type == float:
                    val = settings_config.getfloat(field.name)
                else:
                    val = field.type(settings_config[field.name])
                setattr(self, field.name, val)

    def save(self):
        config = self._make_config()
        with open(self.settings_file, 'w') as configfile:
            config.write(configfile)

    def _make_config(self):
        config = ConfigParser()
        config['Settings'] = {}
        settings_config = config['Settings']
        for field_name in self.__dataclass_fields__.keys():
            settings_config[field_name] = str(getattr(self, field_name))
        return config

    def clear(self):
        for field in self.__dataclass_fields__.values():
            setattr(self, field.name, field.default)
