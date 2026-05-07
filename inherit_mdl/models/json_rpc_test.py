import json
import urllib.request
import random

URL = "http://localhost:1119/jsonrpc"
DB = "200426_v19"
USERNAME = "admin"
PASSWORD = "admin"

def json_rpc(service, method, args):
    payload = {
        "jsonrpc": "2.0",
        "method": service,
        "params": {
            "service": service,
            "method": method,
            "args": args
        },
        "id": random.randint(1,1000)
    }

    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )

    response = json.loads(urllib.request.urlopen(req).read().decode())

    if response.get("error"):
        raise Exception(response["error"])

    return response["result"]

uid = json_rpc("common", "login", [DB, USERNAME, PASSWORD])
print("Logged in UID:", uid)

product_id = json_rpc(
    "object",
    "execute",
    [
        DB,
        uid,
        PASSWORD,
        "product.product",
        "create",
        {
            "name": "Lip tint",
            "purchase_ok": True,
            "type": 'consu',
        }
    ]
)
print("Logged in Product ID:", product_id)


po_id = json_rpc(
    "object",
    "execute",
    [
        DB,
        uid,
        PASSWORD,
        "purchase.order",
        "create",
        {
            "partner_id": 3,
            "order_line": [
                (0, 0, {
                    "product_id": product_id,
                    "product_qty": 10,
                    "price_unit": 100
                })
            ]
        }
    ]
)
print("PO Created:", po_id)


json_rpc(
    "object",
    "execute",
    [
        DB,
        uid,
        PASSWORD,
        "purchase.order",
        "button_confirm",
        [po_id]
    ]
)
print("PO Confirmed")

picking_data = json_rpc(
    "object",
    "execute",
    [
        DB,
        uid,
        PASSWORD,
        "purchase.order",
        "read",
	[po_id],
	["picking_ids"]
    ]
)

picking_id=picking_data[0]["picking_ids"][0]
print("Picking ID:", picking_id)

moves = json_rpc(
    "object",
    "execute",
    [
        DB, uid, PASSWORD,
        "stock.move",
        "search_read",
        [["picking_id", "=", picking_id]],
        ["id", "product_uom_qty", "quantity"]
    ]
)

for move in moves:
    if move["product_uom_qty"] > (move["quantity"] or 0):
        json_rpc(
            "object",
            "execute",
            [
                DB, uid, PASSWORD,
                "stock.move",
                "write",
                [[move["id"]], {
                    "quantity": move["product_uom_qty"]
                }]
            ]
        )
print("Set Quantity")

json_rpc(
    "object",
    "execute",
    [
        DB,
        uid,
        PASSWORD,
        "stock.picking",
        "button_validate",
        [picking_id]
    ]
)
print("Validate")