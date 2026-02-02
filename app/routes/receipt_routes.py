"""
receipt_routes.py

This file exists because app/main.py imports it.
Right now, "receipts" are handled inside attachments_routes.py,
so we re-export that router here to keep imports stable.
"""

from app.routes.attachments_routes import router  # re-export
