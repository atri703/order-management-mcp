from fastmcp import FastMCP

from database import (
    add_note as db_add_note,
    cancel_order as db_cancel_order,
    get_customer_orders as db_get_customer_orders,
    get_order as db_get_order,
    update_status as db_update_status,
)
from permissions import require_scope

mcp = FastMCP("Order Management MCP")


def permission_error_response(exc: PermissionError) -> dict:
    return {"success": False, "error": str(exc)}


@mcp.tool
def get_order(order_id: str, token: str) -> dict:
    """Look up one order. Requires orders:read."""
    try:
        identity = require_scope(token, "orders:read")
    except PermissionError as exc:
        return permission_error_response(exc)

    order = db_get_order(order_id)
    if not order:
        return {"success": False, "message": "Order not found"}

    return {
        "success": True,
        "requested_by": identity["user"],
        "order": order,
    }


@mcp.tool
def list_customer_orders(customer_name: str, token: str) -> dict:
    """List all orders for a customer. Requires orders:read."""
    try:
        identity = require_scope(token, "orders:read")
    except PermissionError as exc:
        return permission_error_response(exc)

    orders = db_get_customer_orders(customer_name)
    return {
        "success": True,
        "requested_by": identity["user"],
        "count": len(orders),
        "orders": orders,
    }


@mcp.tool
def update_order_status(order_id: str, status: str, token: str) -> dict:
    """Update order status. Requires orders:write."""
    try:
        identity = require_scope(token, "orders:write")
    except PermissionError as exc:
        return permission_error_response(exc)

    allowed_statuses = {"PENDING", "PROCESSING", "SHIPPED", "DELIVERED"}
    status = status.upper()

    if status not in allowed_statuses:
        return {
            "success": False,
            "message": f"Invalid status. Allowed: {sorted(allowed_statuses)}",
        }

    if not db_update_status(order_id, status):
        return {"success": False, "message": "Order not found"}

    return {
        "success": True,
        "updated_by": identity["user"],
        "order_id": order_id,
        "new_status": status,
    }


@mcp.tool
def add_order_note(order_id: str, note: str, token: str) -> dict:
    """Add or replace an internal order note. Requires orders:write."""
    try:
        identity = require_scope(token, "orders:write")
    except PermissionError as exc:
        return permission_error_response(exc)

    if not note.strip():
        return {"success": False, "message": "Note cannot be empty"}

    if len(note) > 500:
        return {
            "success": False,
            "message": "Note cannot exceed 500 characters",
        }

    if not db_add_note(order_id, note.strip()):
        return {"success": False, "message": "Order not found"}

    return {
        "success": True,
        "updated_by": identity["user"],
        "order_id": order_id,
    }


@mcp.tool
def cancel_order(order_id: str, token: str) -> dict:
    """Cancel an order. Requires privileged orders:cancel scope."""
    try:
        identity = require_scope(token, "orders:cancel")
    except PermissionError as exc:
        return permission_error_response(exc)

    order = db_get_order(order_id)
    if not order:
        return {"success": False, "message": "Order not found"}

    if order["status"] == "DELIVERED":
        return {
            "success": False,
            "message": "Delivered orders cannot be cancelled",
        }

    if order["status"] == "CANCELLED":
        return {
            "success": False,
            "message": "Order is already cancelled",
        }

    db_cancel_order(order_id)

    return {
        "success": True,
        "cancelled_by": identity["user"],
        "order_id": order_id,
        "new_status": "CANCELLED",
    }


if __name__ == "__main__":
    mcp.run()
