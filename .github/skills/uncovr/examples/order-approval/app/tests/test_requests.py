import unittest

from src.requests import Request, approve, reject


class ApprovalTests(unittest.TestCase):
    def test_pending_request_is_approved(self):
        request = approve(Request("R1", 100, "ana@ops"), "bob@ops")
        self.assertEqual(request.status, "approved")

    def test_requester_cannot_approve_own_request(self):
        with self.assertRaises(PermissionError):
            approve(Request("R2", 100, "ana@ops"), "ana@ops")

    def test_rejected_request_cannot_be_approved(self):
        request = reject(Request("R3", 100, "ana@ops"), "bob@ops")
        with self.assertRaises(ValueError):
            approve(request, "bob@ops")
