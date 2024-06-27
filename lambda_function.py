from logging import getLogger 
import typing as t

from pydantic import BaseModel, ValidationError

from methods import methods, MethodError

log = getLogger(__name__)

class JRPCRequest(BaseModel):
    jsonrpc: t.Literal["2.0"]
    method: str
    params: list[str]
    id: int

    def run_method(self):
        if method := methods.get(self.method):
            try:
                return method(*self.params)
            
            except MethodError as e:
                return str(e)
        
        else:
            raise ValueError(f"Unrecognised method: {self.method}")

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
    if body := event.get("body", None):
        try:
            request_obj = JRPCRequest.model_validate_json(body)
        
        except ValidationError as e:
            log.critical(f"Could not parse event body {body}, error {e}")
            return None
        
        try:
            ret = request_obj.run_method()

            return JRPCResponse(
                result = ret,
                id=request_obj.id
            )
        
        except Exception as e:
            return JRPCError(
                error=str(e),
                id=request_obj.id
            )
    
    else:
        log.info(f"Event {event} lacked body field, assuming it is cors preflight and returning null")
        return None

if __name__=="__main__":
    breakpoint()
    pass