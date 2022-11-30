import math


class BaseDbAccessor:
    def __init__(self) -> None:
        self.limit = 10
        self.offset = 0

    def do_pagination(self, queryset, request):
        limit = int(request.get('limit', self.limit))
        offset = int(request.get('offset', self.offset))

        # limit 0 : takes all objects
        if limit == 0:
            limit = queryset.count()

        total_page = 0
        if limit > 0:
            total_page = math.ceil(queryset.count() / limit)

        return {
            'data': queryset[offset:min(offset+limit, queryset.count())],
            'metadata': {
                'total_items': queryset.count(),
                'total_page': total_page
            }
        }
