"""
Pagination utilities for API endpoints
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Query
from math import ceil


def paginate(
    query: Query,
    page: int = 1,
    per_page: int = 50,
    max_per_page: int = 100
) -> Dict[str, Any]:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (starts at 1)
        per_page: Items per page
        max_per_page: Maximum items per page
        
    Returns:
        Dictionary with items, pagination metadata
    """
    # Validate inputs
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    # Get total count
    total = query.count()
    
    # Calculate pages
    pages = ceil(total / per_page) if total > 0 else 1
    
    # Get items for current page
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
    }

