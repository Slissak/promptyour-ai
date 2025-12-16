"""
Authentication dependencies
"""
from backend.app.api.v1.dependencies.auth_proxy import get_current_user_from_proxy, get_current_user_id_from_proxy_optional

# Re-export the proxy-based dependencies
get_current_user = get_current_user_from_proxy
get_current_user_id_optional = get_current_user_id_from_proxy_optional
