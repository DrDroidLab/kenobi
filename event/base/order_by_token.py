from typing import Dict

from django.db.models import Q, F

from event.base.token import Token, ColumnToken, Annotable, ExpressionTokenizer
from protos.event.query_base_pb2 import Op, OrderByExpression, SortOrder


class OrderByToken(Token):
    order_by: Token = None
    sort_order: SortOrder = None
    allow_nulls = True
    nulls_last = True

    def __init__(self, order_by: Token, sort_order: SortOrder = SortOrder.DESC, allow_nulls=True, nulls_last=True):
        self.order_by = order_by
        self.sort_order = sort_order
        self.allow_nulls = allow_nulls
        self.nulls_last = nulls_last

    def display(self):
        return f'({self.order_by.display()}'


class OrderByTokenAnnotator:
    def annotations(self, t: Token) -> Dict:
        if not isinstance(t, OrderByToken):
            raise ValueError('FilterTokenAnnotator can only process valid OrderBy Expression')
        annotations = {}

        if t.order_by and isinstance(t.order_by, Annotable):
            annotations.update(t.order_by.annotations())

        return annotations


class OrderByTokenizer:
    def __init__(self, columns):
        self._columns = columns
        self._expression_tokenizer = ExpressionTokenizer(columns)

    def tokenize(self, order_by_expression: OrderByExpression) -> OrderByToken:
        if order_by_expression.ByteSize() == 0:
            return

        order_by_token = self._expression_tokenizer.tokenize(order_by_expression.expression)

        allow_nulls = True
        if order_by_expression.allow_nulls:
            allow_nulls = order_by_expression.allow_nulls.value

        nulls_last = True
        if order_by_expression.nulls_last:
            nulls_last = order_by_expression.nulls_last.value

        return OrderByToken(
            order_by=order_by_token,
            sort_order=order_by_expression.order,
            allow_nulls=allow_nulls,
            nulls_last=nulls_last
        )


class OrderByTokenValidator:
    def validate(self, order_by_token: OrderByToken) -> (bool, str):
        if not order_by_token:
            return True, ''
        if not isinstance(order_by_token.order_by, ColumnToken):
            return False, 'Can only order by on columns'

        if not order_by_token.order_by.column.is_orderable:
            return False, 'Selected column is not orderable'
        return True, ''


class OrderByTokenEvaluator:
    def __init__(self):
        self._order_by_token_annotator = OrderByTokenAnnotator()

    def process(self, qs, order_by_token: OrderByToken):
        if not order_by_token:
            return qs

        if isinstance(order_by_token.order_by, Annotable):
            annotations = self._order_by_token_annotator.annotations(order_by_token)
            qs = qs.annotate(**annotations)

        if not order_by_token.allow_nulls:
            qs = qs.filter(
                Q(**{f'{order_by_token.order_by.column_identifier.name}__isnull': order_by_token.allow_nulls}))

        if order_by_token.sort_order == SortOrder.DESC:
            if order_by_token.nulls_last:
                qs = qs.order_by(F(order_by_token.order_by.column_identifier.name).desc(nulls_last=True))
            else:
                qs = qs.order_by(F(order_by_token.order_by.column_identifier.name).desc(nulls_first=True))
        elif order_by_token.sort_order == SortOrder.ASC:
            if order_by_token.nulls_last:
                qs = qs.order_by(F(order_by_token.order_by.column_identifier.name).asc(nulls_last=True))
            else:
                qs = qs.order_by(F(order_by_token.order_by.column_identifier.name).asc(nulls_first=True))

        return qs


class OrderByEngine:
    def __init__(self, columns, default_order_expression: OrderByExpression):
        self.columns = columns
        self.default_order_expression = default_order_expression
        self._order_by_tokenizer = OrderByTokenizer(columns)
        self._order_by_token_validator = OrderByTokenValidator()
        self._order_by_token_evaluator = OrderByTokenEvaluator()

    def tokenize(self, order_by_expression: OrderByExpression) -> OrderByToken:
        return self._order_by_tokenizer.tokenize(order_by_expression)

    def validate(self, filter_token: OrderByToken) -> (bool, str):
        return self._order_by_token_validator.validate(filter_token)

    def evaluate(self, qs, filter_token: OrderByToken):
        return self._order_by_token_evaluator.process(qs, filter_token)

    def process(self, qs, order_by_expression: OrderByExpression):
        if order_by_expression.ByteSize() == 0:
            order_by_expression = self.default_order_expression
        order_by_token: OrderByToken = self.tokenize(order_by_expression)
        if not order_by_token:
            return qs
        order_by_validation_check, err = self.validate(order_by_token)
        if not order_by_validation_check:
            raise ValueError(err)
        return self.evaluate(qs, order_by_token)
