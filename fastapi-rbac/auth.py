from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

roles_hierarchy = ["Member", "Elder", "Co-Leader", "Leader"]

def rbac_dependency(required_role: str):
    def dependency(creds: HTTPAuthorizationCredentials = Depends(security)):
        if creds.credentials == "8882ab1ef43e6107498389f7c5490563":
            role = "Leader"
        elif creds.credentials == "d97f2fc30e804ad1c9509cecede601e8":
            role = "Co-Leader"
        elif creds.credentials == "b9036e63783751545fc2d8a6edcca5b7":
            role = "Elder"
        elif creds.credentials == "b00912b712b2176ece1783c11fdf6265":
            role = "Member"
        else:
            raise HTTPException(status_code=400, detail="Invalid role.")
        if roles_hierarchy.index(role) < roles_hierarchy.index(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. '{role}' cannot access '{required_role}' endpoint."
            )
        return role
    return dependency

def is_leader_dependency(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds.credentials == "8882ab1ef43e6107498389f7c5490563":
        return True
    raise HTTPException(status_code=403, detail="Only Leader can access this endpoint.")