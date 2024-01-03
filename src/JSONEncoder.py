
import json

# use `json.dumps(object,cls=JSONEncoder,indent=4)`
# to recursively dump the object, but keep the option
# to leave certain unserialzables out of the export

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'toJSON'):
            return obj.toJSON()
        else:
            return vars(obj)