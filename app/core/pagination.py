from urllib.parse import urlencode


def build_pagination(
    *,
    page: int,
    per_page: int,
    total: int,
    base_path: str,
    query_params: dict[str, str | int | bool | None],
) -> dict[str, object | None]:
    total_pages = max(1, (total + per_page - 1) // per_page)

    def _make_link(target_page: int) -> str:
        params = {k: v for k, v in query_params.items() if v is not None}
        params.update({'page': target_page, 'per_page': per_page})
        return f"{base_path}?{urlencode(params)}"

    next_link = _make_link(page + 1) if page < total_pages else None
    prev_link = _make_link(page - 1) if page > 1 else None

    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'next': next_link,
        'prev': prev_link,
    }