import sys

is_jython = sys.platform.startswith("java")

if not is_jython:
    import uacalc_lib

    _lat = getattr(uacalc_lib, "lat")

    for _name in dir(_lat):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_lat, _name)

    _lattice_from_join = globals()["lattice_from_join"]
    _lattice_from_meet = globals()["lattice_from_meet"]

    class Lattices(object):
        """Static facade matching Java ``org.uacalc.lat.Lattices``."""

        @staticmethod
        def latticeFromJoin(name, join_op):
            return _lattice_from_join(name, join_op)

        @staticmethod
        def latticeFromMeet(name, meet_op):
            return _lattice_from_meet(name, meet_op)

    globals()["Lattices"] = Lattices
else:
    from org.uacalc.lat import *  # noqa: F403
