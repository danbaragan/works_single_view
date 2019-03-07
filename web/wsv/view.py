from flask_restful import Resource

from .db import *
from .serializer import *


class WorksList(Resource):
    def get(self):
        works_q = Work.select()
        works = works_schema.dump(works_q).data
        return {
            'works': works
        }
