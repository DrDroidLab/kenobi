from django.db.models import Aggregate, Func


class Percentile(Aggregate):
    function = "PERCENTILE_CONT"
    name = "Percentile"
    template = "%(function)s (%(percentile)s) WITHIN GROUP (ORDER BY %(expressions)s)"


class DistinctFunc(Func):
    template = "%(function)s(DISTINCT %(expressions)s)"
