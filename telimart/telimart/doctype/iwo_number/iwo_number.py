# Copyright (c) 2025, Telimart
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IWONumber(Document):

    def on_update(self):
        """
        Auto-share IWO with team members on save/update
        """
        if not self.team_members:
            return

        for row in self.team_members:
            if not row.user:
                continue

            # Check if already shared
            already_shared = frappe.db.exists(
                "DocShare",
                {
                    "share_doctype": self.doctype,
                    "share_name": self.name,
                    "user": row.user
                }
            )

            if not already_shared:
                frappe.share.add(
                    self.doctype,
                    self.name,
                    row.user,
                    read=1,
                    write=1,
                    share=1,
                    notify=1
                )

        # Remove users no longer in team
        self.remove_unused_shares()

    def on_trash(self):
        """
        Remove all shares when IWO is deleted
        """
        frappe.db.delete(
            "DocShare",
            {
                "share_doctype": self.doctype,
                "share_name": self.name
            }
        )

    def remove_unused_shares(self):
        """
        Remove DocShare entries for users removed from team
        """
        team_users = [d.user for d in self.team_members if d.user]

        existing_shares = frappe.db.get_all(
            "DocShare",
            filters={
                "share_doctype": self.doctype,
                "share_name": self.name
            },
            fields=["user"]
        )

        for share in existing_shares:
            if share.user not in team_users:
                frappe.share.remove(
                    self.doctype,
                    self.name,
                    share.user
                )
