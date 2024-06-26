import typing as t

from pydantic import BaseModel

from methods import methods, MethodError

class JRPCRequest(BaseModel):
    jsonrpc: t.Literal["2.0"]
    method: str
    params: tuple[str, ...]
    id: int

class JRPCResponse(BaseModel):
    result: str
    id: int
    jsonrpc: t.Literal["2.0"] = "2.0"

class JRPCError(BaseModel):
    jsonrpc: t.Literal["2.0"] = "2.0"
    error: str
    id: int

def lambda_handler(event: dict, context) -> JRPCResponse | JRPCError | None:
    try:
        request_obj = JRPCRequest.model_validate(event)
    
    except:
        return None

    if method := methods.get(request_obj.method, None):
        try:
            ret = method(request_obj.params)

            return JRPCResponse(
                result=ret,
                id=request_obj.id,
            )

        except MethodError as e:
            return JRPCError(
                error=str(e),
                id=request_obj.id,
            )
    
    else:
        return JRPCError(
            error=f"Unrecognised method {request_obj.method}",
            id=request_obj.id
        )

