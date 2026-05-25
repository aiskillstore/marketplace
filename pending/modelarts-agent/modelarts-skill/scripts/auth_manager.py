#!/usr/bin/env python3
"""
ModelArts Authentication Manager

Implements intelligent authentication with automatic environment detection:
- Notebook Mode: Auto-retrieves credentials from ModelArts session
- Local Mode: Prompts for manual AK/SK input (memory-only storage)
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, Tuple


if os.path.exists('/modelarts/tools/sdk'):
    if '/modelarts/tools/sdk' not in sys.path:
        sys.path.insert(0, '/modelarts/tools/sdk')
elif os.path.exists('/modelarts/authoring/notebook-conda/envs/jp3/lib/python3.9/site-packages'):
    if '/modelarts/authoring/notebook-conda/envs/jp3/lib/python3.9/site-packages' not in sys.path:
        sys.path.insert(0, '/modelarts/authoring/notebook-conda/envs/jp3/lib/python3.9/site-packages')


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AuthManager:
    """
    Manages ModelArts authentication with environment auto-detection.
    """
    
    def __init__(self):
        self._credentials: Optional[Dict[str, str]] = None
        self._environment: str = "unknown"
        self._session = None
        self._initialized: bool = False
        
    def detect_environment(self) -> str:
        """
        Detect if running in ModelArts Notebook environment.
        
        Returns:
            'notebook' if in ModelArts Notebook, 'local' otherwise
        """
        try:
            from modelarts.session import Session
            session = Session()
            # Try to access credentials - will fail if not in notebook
            _ = session.access_key
            _ = session.secret_key
            _ = session.project_id
            _ = session.region_name
            self._environment = "notebook"
            self._session = session
            return "notebook"
        except Exception:
            self._environment = "local"
            return "local"
    
    def get_credentials(self, ak: str = None, sk: str = None, 
                       project_id: str = None, region: str = None,
                       security_token: str = None) -> Dict[str, str]:
        """
        Get credentials based on environment.
        
        Args:
            ak: Access Key (required for local mode)
            sk: Secret Key (required for local mode)
            project_id: Project ID (required for local mode)
            region: Region name (required for local mode)
            security_token: Security token (auto-set in notebook mode)
            
        Returns:
            Dict with credentials (INTERNAL USE ONLY)
            
        Raises:
            ValueError: If required credentials are missing
        """
        if self._credentials:
            return self._credentials
            
        env = self.detect_environment()
        
        if env == "notebook":
            self._credentials = {
                "ak": self._session.access_key,
                "sk": self._session.secret_key,
                "project_id": self._session.project_id,
                "region": self._session.region_name,
                "security_token": getattr(self._session, 'security_token', None),
                "environment": "notebook"
            }
            self._initialized = True
            logger.info("Notebook mode: credentials auto-loaded (values hidden)")
        else:
            if not all([ak, sk, project_id, region]):
                raise ValueError(
                    "Local mode requires AK, SK, PROJECT_ID, and REGION. "
                    "Please provide credentials or run within ModelArts Notebook."
                )
            self._credentials = {
                "ak": ak,
                "sk": sk,
                "project_id": project_id,
                "region": region,
                "security_token": security_token,
                "environment": "local"
            }
            self._initialized = True
            logger.info("Local mode: credentials set (values hidden)")
        
        return self._credentials
    
    def get_session(self):
        """
        Get authenticated ModelArts session.
        
        Returns:
            Authenticated session object or None
        """
        if self._environment == "notebook" and self._session:
            return self._session
        return None
    
    def clear_credentials(self):
        """Clear stored credentials (security cleanup)."""
        if self._credentials:
            # Securely clear from memory
            for key in self._credentials:
                self._credentials[key] = None
            self._credentials = None
    
    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get authentication status info - SAFE FOR LLM.
        Returns:
            Dict with auth status (masked, safe for logging/LLM)
        """
        if not self._credentials:
            return {"authenticated": False, "environment": self._environment}
        
        info = {
            "authenticated": True,
            "environment": self._credentials.get("environment", "unknown"),
            "project_id": self._credentials.get("project_id", "unknown"),
            "region": self._credentials.get("region", "unknown"),
        }
        
        # ALWAYS mask AK - never return raw value
        if self._credentials.get("ak"):
            ak = self._credentials["ak"]
            info["ak_masked"] = f"{ak[:6]}***{ak[-4:]}" if len(ak) > 10 else "***"
        
        # Indicate if security token is present (without exposing it)
        if self._credentials.get("security_token"):
            info["has_security_token"] = True
        
        return info


class SDKCalls:
    """
    Secure wrapper for ModelArts SDK method calls.
    
    MODE: SDK Call Mode
    - Uses ModelArts SDK's high-level API methods
    - Session handles all authentication internally
    - Credentials never exposed to caller
    """
    
    def __init__(self, auth_manager: AuthManager):
        self._auth = auth_manager
        
    def get_session(self) -> Any:
        """
        Get authenticated session for SDK calls.
        """
        if not self._auth._initialized and self._auth._environment != "notebook":
            raise RuntimeError("Authentication not initialized. Call ma_auth_initialize first.")
        
        if self._auth._environment == "notebook":
            return self._auth._session
        else:
            # Create session from stored credentials (credentials never exposed)
            from modelarts.session import Session
            creds = self._auth._credentials
            return Session(
                access_key=creds["ak"],
                secret_key=creds["sk"],
                project_id=creds["project_id"],
                region=creds["region"],
                security_token=creds.get("security_token")
            )
    
    def execute(self, sdk_func, *args, **kwargs) -> Any:
        """
        Execute an SDK function with authenticated session.
        Args:
            sdk_func: SDK function to call (receives session as first arg)
            *args, **kwargs: Arguments to pass to SDK function
            
        Returns:
            SDK function result (should be safe data, not credentials)
        """
        session = self.get_session()
        return sdk_func(session, *args, **kwargs)


class APIGDirectCalls:
    """
    Secure wrapper for direct APIG (API Gateway) direct HTTP calls.
    
    MODE: APIG Direct Call Mode
    - Calls ModelArts API directly via HTTP/HTTPS
    - Uses ModelArts SDK's auth_by_apig for automatic request signing
    - Adds required headers automatically (x-modelarts-user-id, x-security-token)
    - Credentials never exposed to caller
    """
    
    def __init__(self, auth_manager: AuthManager):
        self._auth = auth_manager
        
    def execute(self, method: str, path: str, query: Dict[str, Any] = None, 
               body: Dict[str, Any] = None) -> Any:
        """
        Execute a direct APIG API call with automatic signing.
        Args:
            method: HTTP method (GET, POST, PUT, DELETE supported)
            path: API path, can include {project_id} for automatic substitution
            query: Query parameters (optional)
            body: Request body JSON (optional)
            
        Returns:
            API response result
        """
        from modelarts import constant
        from modelarts.config.auth import auth_by_apig
        
        session = self._auth.get_session()
        if not session:
            raise RuntimeError("Authentication not initialized. Call ma_auth_initialize first.")
        
        method_norm = method.upper().strip()
        method_map = {
            "GET": constant.HTTPS_GET,
            "POST": constant.HTTPS_POST,
            "PUT": constant.HTTPS_PUT,
            "DELETE": constant.HTTPS_DELETE
        }
        method_const = method_map.get(method_norm, method_norm)
        
        if "{project_id}" in path and hasattr(session, 'project_id'):
            path = path.format(project_id=session.project_id)
        
        extra_headers = {}
        
        if hasattr(session, 'user_id') and session.user_id:
            extra_headers['x-modelarts-user-id'] = session.user_id
            
        creds = self._auth._credentials
        if creds and creds.get("security_token"):
            extra_headers['x-security-token'] = creds["security_token"]
        
        if body is not None:
            body = json.dumps(body).encode('utf-8')
        
        return auth_by_apig(session, method_const, path, query=query, body=body, headers=extra_headers)


class SecureAccess:
    """
    Combined secure access - provides both modes cleanly.
    
    Tools can choose which mode to use based on API availability:
    - `sdk()` for SDK method calls -> `sdk.execute(func, ...)`
    - `apig()` for direct APIG calls -> `apig.execute(method, path, ...)`
    """
    
    def __init__(self, auth_manager: AuthManager):
        self._auth = auth_manager
        self._sdk: Optional[SDKCalls] = None
        self._apig: Optional[APIGDirectCalls] = None
        
    def sdk(self) -> SDKCalls:
        """Get SDK call mode interface."""
        if self._sdk is None:
            self._sdk = SDKCalls(self._auth)
        return self._sdk
    
    def apig(self) -> APIGDirectCalls:
        """Get APIG direct call mode interface."""
        if self._apig is None:
            self._apig = APIGDirectCalls(self._auth)
        return self._apig


_auth_manager: Optional[AuthManager] = None
_secure_sdk: Optional[SecureAccess] = None


def get_auth_manager() -> AuthManager:
    """Get the singleton AuthManager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


def get_secure_access() -> SecureAccess:
    """
    Get secure access interface - provides both SDK and APIG modes.
    Usage:
        access = get_secure_access()
        # For SDK calls:
        result = access.sdk().execute(my_sdk_func, arg1, arg2)
        # For APIG direct calls:
        result = access.apig().execute("GET", "/v1/{project_id}/notebooks/all", query={"size": 10})
    """
    global _secure_sdk
    if _secure_sdk is None:
        _secure_sdk = SecureAccess(get_auth_manager())
    return _secure_sdk

def get_secure_sdk() -> SecureAccess:
    """Alias for get_secure_access - backward compatibility."""
    return get_secure_access()


def create_session(ak: str = None, sk: str = None, 
                   project_id: str = None, region: str = None,
                   security_token: str = None):
    """
    Create an authenticated ModelArts session.
    Args:
        ak: Access Key (optional, auto-detected in notebook)
        sk: Secret Key (optional, auto-detected in notebook)
        project_id: Project ID (optional, auto-detected in notebook)
        region: Region name (optional, auto-detected in notebook)
        security_token: Security token (optional)
        
    Returns:
        Tuple of (success: bool, session_or_error: Any)
    """
    try:
        auth = get_auth_manager()
        creds = auth.get_credentials(
            ak=ak, sk=sk, 
            project_id=project_id, region=region,
            security_token=security_token
        )
        
        if creds["environment"] == "notebook":
            session = auth.get_session()
            return True, session
        else:
            from modelarts.session import Session
            session = Session(
                access_key=creds["ak"],
                secret_key=creds["sk"],
                project_id=creds["project_id"],
                region=creds["region"],
                security_token=creds.get("security_token")
            )
            return True, session
            
    except Exception as e:
        return False, str(e)


def check_auth_status() -> Dict[str, Any]:
    """
    Check current authentication status - SAFE FOR LLM.
    Returns:
        Dict with authentication status info (masked)
    """
    auth = get_auth_manager()
    auth.detect_environment()
    return auth.get_auth_info()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ModelArts Auth Manager")
    parser.add_argument("--check", action="store_true", help="Check auth status")
    parser.add_argument("--ak", help="Access Key (local mode)")
    parser.add_argument("--sk", help="Secret Key (local mode)")
    parser.add_argument("--project-id", help="Project ID (local mode)")
    parser.add_argument("--region", help="Region (local mode)")
    
    args = parser.parse_args()
    
    if args.check:
        status = check_auth_status()
        print(json.dumps(status, indent=2))
    else:
        auth = get_auth_manager()
        env = auth.detect_environment()
        print(f"Environment: {env}")
        
        if env == "notebook":
            print("Running in ModelArts Notebook - credentials auto-detected")
            info = auth.get_auth_info()
            print(json.dumps(info, indent=2))
        else:
            print("Running in local mode - credentials required")
            if args.ak and args.sk and args.project_id and args.region:
                try:
                    creds = auth.get_credentials(
                        ak=args.ak, sk=args.sk,
                        project_id=args.project_id, region=args.region
                    )
                    print("Credentials set successfully (values hidden)")
                    print(json.dumps(auth.get_auth_info(), indent=2))
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Provide --ak, --sk, --project-id, and --region")
