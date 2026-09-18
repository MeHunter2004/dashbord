CLOSED_STATUSES = {'حل شده', 'خاتمه يافته'}
REJECTED_STATUSES = {'رد شده'}

def high_level_status(status: str) -> str:
    status = str(status).strip()
    if status in CLOSED_STATUSES:
        return 'رسیدگی‌شده'
    if status in REJECTED_STATUSES:
        return 'ردشده'
    return 'باز / در جریان'
