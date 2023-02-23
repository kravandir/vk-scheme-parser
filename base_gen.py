from abc import ABC


class BaseMethod(ABC):
    def __init__(self, vk):
        self.vk = vk

    async def method(self, method:str, **params):
        try:
            params.pop('self')
        except: pass
        return await self.vk.call_method(method, **params)
