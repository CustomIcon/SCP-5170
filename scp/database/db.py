class Temp:
    unallowed = [int, float]

    def __init__(
        self,
        schema=None,
        data=dict,
    ):
        self.data = data
        self.schema = schema

    def add(self, key, value):
        if self.data.get(key):
            raise Exception('key exists')

        if not self.schema:
            """
            If a pydantic schema is not set then simply
            add the key and value to cache
            """
            self.data[key] = value
            return True
        else:
            """
            A pydantic schema has been set
            """
            schema = self.schema
            """
            if passed value is of type dict, then use parse_obj
            if its a string, then it must be a json string, so use
            parse_raw
            if not, it has to be a model instance so use from_orm
            """
            if type(value) in self.unallowed:
                raise Exception(f'unallowed type {type(value)}')
            if type(value) is dict:
                schema = self.schema.parse_obj
            elif type(value) is str:
                schema = self.schema.parse_raw
            else:
                schema = self.schema.from_orm
                """
                Validate the model and raise any exceptions
                """
                try:
                    val = schema(value)
                except Exception:
                    raise
            self.data[key] = val

        return True

    def remove(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass
        return True

    def get(self, key):
        try:
            val = self.data[key]
        except KeyError:
            raise Exception('key does not exist')
        return val
