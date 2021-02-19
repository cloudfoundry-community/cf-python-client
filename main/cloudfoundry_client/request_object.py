class Request(dict):
    def __setitem__(self, key, value):
        if value is not None:
            super(Request, self).__setitem__(key, value)
