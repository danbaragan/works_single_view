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


class WorksDetail(Resource):
    def get(self, iswc):
        try:
            w = Work.get(Work.iswc == iswc)
        except Work.DoesNotExist:
            return {}, 404
        work = work_schema.dump(w).data
        return {
            'work': work
        }
