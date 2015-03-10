from uuid import uuid4, UUID

from sqlalchemy import Column, Unicode
from sqlalchemy_utils import UUIDType

from unicore.hub.service import Base


class UUIDMixin(object):
    _uuid = Column(
        UUIDType(binary=False), name='uuid', default=uuid4,
        primary_key=True)

    @property
    def uuid(self):
        return self._uuid.hex

    @uuid.setter
    def uuid(self, value):
        if isinstance(value, UUID):
            self._uuid = value
        else:
            self._uuid = UUID(hex=value)


class Question(Base, UUIDMixin):
    __tablename__ = 'questions'

    title = Column(Unicode(255), nullable=False)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
        }
