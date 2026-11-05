"""
Topic 4: Endpoints & Request Inputs
===================================

Key Concepts Explained:
-----------------------
1. What is an Endpoint?
   - While the Route specifies the URL path & HTTP Method (e.g. `POST /chat`),
     the Endpoint is the actual Python function attached to it!
   - The endpoint holds the "business logic" (validating inputs, querying DB, calling AI models).

2. How Endpoints Receive Input:
   FastAPI allows 3 primary ways to pass data into an endpoint:
   a) Path Parameters:  Variables embedded in the URL path (e.g., `/items/{item_id}`).
   b) Query Parameters: Key-value pairs after the '?' in URL (e.g., `/search?query=ai&limit=10`).
   c) Request Body:     JSON payload sent in the HTTP body (parsed and validated by Pydantic).

3. Return Values:
   - Python dictionaries, lists, or Pydantic models are automatically converted to JSON.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/04_endpoints_and_inputs.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Topic 4: Endpoints & Request Handling",
    description="Demonstrating Path Parameters, Query Parameters, and Request Bodies.",
    version="1.0.0",
)


# Pydantic Model for Request Body validation
class Product(BaseModel):
    name: str = Field(..., example="Wireless Noise-Cancelling Headphones")
    category: str = Field(..., example="Electronics")
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    in_stock: bool = True
    tags: list[str] = []


# Sample catalog
products_catalog = [
    {"id": 1, "name": "Python Book", "category": "Books", "price": 29.99, "in_stock": True, "tags": ["coding"]},
    {"id": 2, "name": "Mechanical Keyboard", "category": "Electronics", "price": 89.99, "in_stock": True, "tags": ["hardware"]},
    {"id": 3, "name": "AI Assistant Device", "category": "Electronics", "price": 129.99, "in_stock": False, "tags": ["ai", "gadget"]},
]


# -------------------------------------------------------------------
# 1. Path Parameters: Extracting variables from the URL path
# -------------------------------------------------------------------
@app.get("/products/{product_id}", tags=["Endpoints"])
def get_product_by_id(
    product_id: int = Path(..., title="The ID of the product", ge=1)
):
    """
    Endpoint demonstrating a PATH parameter.
    `product_id` is part of the URL path: /products/1
    """
    for item in products_catalog:
        if item["id"] == product_id:
            return {"status": "success", "product": item}
    return {"status": "not_found", "message": f"Product {product_id} was not found."}


# -------------------------------------------------------------------
# 2. Query Parameters: Filtering, searching, and pagination
# -------------------------------------------------------------------
@app.get("/products", tags=["Endpoints"])
def filter_products(
    category: str | None = Query(None, description="Filter by category (e.g. Electronics)"),
    max_price: float | None = Query(None, description="Maximum price filter"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
):
    """
    Endpoint demonstrating QUERY parameters.
    Example URL: /products?category=Electronics&max_price=100&limit=5
    Notice default values and optional types!
    """
    results = products_catalog
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    return {
        "filters_applied": {"category": category, "max_price": max_price, "limit": limit},
        "count": len(results[:limit]),
        "items": results[:limit],
    }


# -------------------------------------------------------------------
# 3. Request Body + Path Param combined: Business logic execution
# -------------------------------------------------------------------
@app.post("/products", tags=["Endpoints"])
def add_new_product(product: Product):
    """
    Endpoint demonstrating REQUEST BODY parsing with Pydantic validation.
    The endpoint function receives a fully validated `Product` object.
    """
    # Business Logic: Calculate tax and assign new ID
    tax = round(product.price * 0.10, 2)
    final_price = round(product.price + tax, 2)

    new_id = len(products_catalog) + 1
    new_product_dict = {
        "id": new_id,
        **product.model_dump(),
        "tax": tax,
        "final_price": final_price,
    }
    products_catalog.append(new_product_dict)

    return {
        "message": "Product validated and registered successfully!",
        "product": new_product_dict,
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 4 Demo Server Starting!")
    print("👉 Explore Path Params, Query Params & Body in Swagger UI:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("04_endpoints_and_inputs:app", host="127.0.0.1", port=8000, reload=True)
