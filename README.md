# Global search plugin

# Installation

Update your invenio.cfg file:

```python
from oarepo_global_search.proxies import global_search_view_function

SEARCH_UI_SEARCH_VIEW = global_search_view_function
```

# Usage

Head to `/search` to see the global search in action. On the API level,
`/api/search` gives you the API access, `/api/user/search` gives you the 
search that limits the records to yours.

# Configuration