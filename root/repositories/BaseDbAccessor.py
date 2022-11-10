class BaseDbAccessor:
    def __init__(self) -> None:
        self.limit = 20
        self.offset = 0

    def do_query(self, queryset, request):
        limit = request.get('limit', self.limit)
        offset = request.get('offset', self.offset)

        if offset+limit > queryset.count():
            limit = queryset.count() - offset

        if request.get('order_by') is not None:
            queryset = queryset.order_by(request.get('order_by'))
        if request.get('sort_by') is not None:
            queryset = queryset.order_by(request.get('sort_by'))
        queryset = queryset[offset:offset+limit]
        return queryset
