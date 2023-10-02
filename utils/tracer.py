from decorator import contextmanager


class NoopSpan:
    def set_tag(self, *args, **kwargs):
        return

    def set_traceback(self):
        return


class NoopTracer:
    @contextmanager
    def trace(self, name):
        try:
            yield NoopSpan()
        finally:
            pass


tracer = NoopTracer()
try:
    from ddtrace import tracer as dd_tracer

    tracer = dd_tracer
except ImportError:
    pass
