# Order Management MCP Server

A small MCP demo that exposes live order lookup and controlled database-write tools with scoped permissions.

The project uses:

- Python
- FastMCP
- SQLite
- Parameterized SQL
- Simple demo tokens with read, write, and privileged cancel scopes

> The token approach is intentionally simple for local testing. In production, authenticate the MCP connection with OAuth/JWT or an API gateway and derive scopes server-side instead of exposing credentials as tool arguments.

## Permission model

| Identity | Token | Scopes |
|---|---|---|
| Reader | `reader-token` | `orders:read` |
| Operator | `operator-token` | `orders:read`, `orders:write` |
| Admin | `admin-token` | `orders:read`, `orders:write`, `orders:cancel` |

The server enforces permissions before touching the database.

## Available tools

### get_order

Looks up one order.

Required scope:

```
orders:read
```

### list_customer_orders

Lists all orders for a customer.

Required scope:

```
orders:read
```

### update_order_status

Changes an order status.

Required scope:

```
orders:write
```

Allowed statuses:

- PENDING
- PROCESSING
- SHIPPED
- DELIVERED

### add_order_note

Adds or replaces an internal note.

Required scope:

```
orders:write
```

Notes are limited to 500 characters.

### cancel_order

Cancels an order.

Required scope:

```
orders:cancel
```

Delivered orders cannot be cancelled.

## Dummy data

Running `seed.py` creates:

| Order | Customer | Product | Amount | Status |
|---|---|---|---:|---|
| ORD-1001 | Atri Gulati | MacBook Pro | 189999 | PROCESSING |
| ORD-1002 | Rahul Sharma | iPhone 17 | 89999 | SHIPPED |
| ORD-1003 | Priya Singh | AirPods Pro | 24999 | DELIVERED |
| ORD-1004 | Atri Gulati | Magic Mouse | 8999 | PENDING |
| ORD-1005 | Neha Verma | iPad Air | 69999 | PROCESSING |

## Setup

Clone the repository:

```bash
git clone https://github.com/atri703/order-management-mcp.git
cd order-management-mcp
```

Create a virtual environment:

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed the database:

```bash
python seed.py
```

Start the MCP server:

```bash
python server.py
```

## Sample test queries

These prompts assume the MCP client/agent is connected to this server and supplies the indicated demo token.

### 1. Read one order

Token:

```
reader-token
```

Prompt:

```
Find order ORD-1001 and show me its details.
```

Expected: success.

### 2. List customer orders

Token:

```
reader-token
```

Prompt:

```
Show me all orders belonging to Atri Gulati.
```

Expected orders:

- ORD-1001
- ORD-1004

### 3. Reader attempts a write

Token:

```
reader-token
```

Prompt:

```
Change ORD-1001 status to SHIPPED.
```

Expected:

```
Permission denied. Required scope: orders:write
```

### 4. Operator performs a write

Token:

```
operator-token
```

Prompt:

```
Change ORD-1001 status to SHIPPED.
```

Expected: success.

### 5. Operator adds a note

Token:

```
operator-token
```

Prompt:

```
Add a note to ORD-1004 saying "Customer requested weekend delivery."
```

Then query the order again to verify the write persisted.

### 6. Operator attempts privileged cancellation

Token:

```
operator-token
```

Prompt:

```
Cancel ORD-1004.
```

Expected:

```
Permission denied. Required scope: orders:cancel
```

### 7. Admin cancels an order

Token:

```
admin-token
```

Prompt:

```
Cancel ORD-1004.
```

Expected: order status becomes `CANCELLED`.

### 8. Business-rule protection

Token:

```
admin-token
```

Prompt:

```
Cancel ORD-1003.
```

ORD-1003 is already delivered, so the server returns:

```
Delivered orders cannot be cancelled
```

## Why the permission check belongs on the MCP server

The model or agent should never be trusted to enforce authorization itself.

The flow is:

```
LLM / Agent
    |
    v
MCP Client
    |
    v
Order Management MCP Server
    |
    +-- get_order ------------ orders:read
    +-- list_customer_orders - orders:read
    +-- update_order_status -- orders:write
    +-- add_order_note ------- orders:write
    +-- cancel_order --------- orders:cancel
    |
    v
SQLite
```

Even if an LLM tries to call `cancel_order`, the server denies the operation unless the authenticated identity has the `orders:cancel` scope.

## Production improvements

For a real backend:

1. Replace SQLite with PostgreSQL or another production database.
2. Replace hard-coded demo tokens with OAuth/JWT authentication.
3. Derive identity and scopes from the authenticated MCP request.
4. Use separate database roles for read-only and write operations.
5. Add audit logging for every write operation.
6. Add approval or confirmation for high-impact tools such as cancellation/refund.
7. Store secrets in a secret manager rather than source code.
8. Add rate limiting and request tracing.
9. Add automated tests for authorization and business rules.

## Resetting the database

To restore the original dummy dataset:

```bash
python seed.py
```

This recreates `orders.db` from scratch.
