"""Purchase request approval."""

APPROVAL_LIMIT = 5000


class Request:
    def __init__(self, request_id, amount, requester):
        self.request_id = request_id
        self.amount = amount
        self.requester = requester
        self.status = "pending"


def approve(request, approver):
    if request.status != "pending":
        raise ValueError("only pending requests can be approved")
    if approver == request.requester:
        raise PermissionError("requesters cannot approve their own request")
    if request.amount > APPROVAL_LIMIT and not approver.endswith("@finance"):
        raise PermissionError("amounts above the limit need finance approval")
    request.status = "approved"
    return request


def reject(request, approver):
    # TODO: notify the requester
    if request.status != "pending":
        raise ValueError("only pending requests can be rejected")
    request.status = "rejected"
    return request
