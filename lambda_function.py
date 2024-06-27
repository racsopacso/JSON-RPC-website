import typing as t

from pydantic import BaseModel, ValidationError

from methods import methods, MethodError

class JRPCRequest(BaseModel):
    jsonrpc: t.Literal["2.0"]
    method: str
    params: list[str]
    id: int

class JRPCResponse(BaseModel):
    result: str
    id: int
    jsonrpc: t.Literal["2.0"] = "2.0"

class JRPCError(BaseModel):
    jsonrpc: t.Literal["2.0"] = "2.0"
    error: str
    id: int

def serialise_object(func: t.Callable[..., BaseModel | None]) -> t.Callable[..., dict | None]:
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)

        if ret:
            dmp = ret.model_dump()
            print(dmp)
            return dmp
        else:
            return None
    
    return inner

@serialise_object
def lambda_handler(event: dict, context) -> JRPCResponse | JRPCError | None:    
    try:
        event = event["body"]
    except KeyError:
        event = event

    try:
        request_obj = JRPCRequest.model_validate_json(event)
    
    except ValidationError as e:
        return JRPCError(
            error=f"Could not validate event: {event} due to {e}",
            id=0,
        )

    if method := methods.get(request_obj.method, None):
        try:
            ret = method(*request_obj.params)

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

if __name__=="__main__":
    breakpoint()
    pass