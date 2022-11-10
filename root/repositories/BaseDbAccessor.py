class BaseDbAccessor:
    def __init__(self) -> None:
        self.limit = 10
        self.offset = 0

    def do_query(self, queryset, request):
        limit = int(request.get('limit', self.limit))
        offset = int(request.get('offset', self.offset))
        order_by = request.get('order_by', '-id')

        if offset+limit > queryset.count():
            limit = queryset.count() - offset

        queryset = queryset.order_by(order_by)
        queryset = queryset[offset:offset+limit]
        return queryset
