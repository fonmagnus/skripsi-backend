import math


class BaseDbAccessor:
    def __init__(self) -> None:
        self.limit = 10
        self.offset = 0

    def do_query(self, queryset, request):
        limit = int(request.get('limit', self.limit))
        offset = int(request.get('offset', self.offset))
        order_by = request.get('order_by', '-id')

        # limit 0 : takes all objects
        if limit == 0:
            limit = queryset.count()

        total_page = 0
        if limit > 0:
            total_page = math.ceil(queryset.count() / limit)
        queryset = queryset.order_by(order_by)
        return {
            'result': queryset[offset:offset+limit],
            'meta': {
                'total_items': queryset.count(),
                'total_page': math.ceil(queryset.count() / limit)
            }
        }
