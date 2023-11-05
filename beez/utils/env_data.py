import environ
import os

root = environ.Path(os.path.basename(__file__) + "../../")
env = environ.Env(DEBUG=(bool, True), )
environ.Env.read_env()


class ENVData:

    @staticmethod
    def get_value(variable):
        return env(variable)
