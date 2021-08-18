import configparser

class WithMetaMixin:
    """
    A mixin representing a model contains a meta file

    It assume that the object contains a field called _folder, which represents the folder
    the model has.
    """

    def _save_meta_data(self, meta: dict):
        """
        Override the meta.ini with what meta dict provides
        """
        config = configparser.ConfigParser()
        config['meta'] = meta
        with open(self._folder / 'meta.ini', 'w') as fr:
            config.write(fr)

    def _read_meta(self, section='meta'):
        """
        Return a dict represents the meta data of the folder
        """
        config = configparser.ConfigParser()
        config.read(self._folder / 'meta.ini')
        return config[section]

    def _set_meta_data(self, field, value, section='meta'):
        """
        Set a value into the meta data field.
        """
        config = configparser.ConfigParser()
        config.read(self._folder / 'meta.ini')
        config[section][field] = value
        with open(self._folder / 'meta.ini', 'w') as fr:
            config.write(fr)