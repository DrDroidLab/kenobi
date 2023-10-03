from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models import Q

from event.engine.context import ContextResolver, get_context_resolver
from event.models import EventType, Monitor, Entity
from protos.event.base_pb2 import Context


class FuzzyMatchEngineException(ValueError):
    pass


class FuzzyMatchEngine:

    def __init__(self, model, context_resolver: ContextResolver):
        self._model = model
        self._context_resolver = context_resolver

    def match_pattern(self, account, pattern: str, similarity_ratio_threshold=0.3):
        qs = self._context_resolver.qs(account)

        return qs.annotate(similarity=TrigramWordSimilarity(pattern, 'name')).filter(
            Q(name__trigram_word_similar=pattern) | Q(similarity__gte=similarity_ratio_threshold)).order_by(
            '-similarity')


event_type_fuzzy_match_engine = FuzzyMatchEngine(
    EventType,
    get_context_resolver(Context.EVENT_TYPE),
)

monitor_fuzzy_match_engine = FuzzyMatchEngine(
    Monitor,
    get_context_resolver(Context.MONITOR),
)

entity_fuzzy_match_engine = FuzzyMatchEngine(
    Entity,
    get_context_resolver(Context.ENTITY),
)
