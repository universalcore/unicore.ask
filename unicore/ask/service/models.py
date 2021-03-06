from uuid import uuid4, UUID

from sqlalchemy import (
    Column, Unicode, Boolean, ForeignKey, Integer, DateTime, func)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


from unicore.ask.service import Base


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


class QuestionResponse(Base, UUIDMixin):
    __tablename__ = 'question_responses'

    text = Column(Unicode(), nullable=False)
    question_id = Column(
        UUIDType(binary=False), ForeignKey('questions.uuid'), nullable=False)
    question_option_id = Column(
        UUIDType(binary=False), ForeignKey('question_options.uuid'),
        nullable=False)
    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now())

    app_uuid = Column(UUIDType(binary=False), nullable=False)
    user_uuid = Column(UUIDType(binary=False), nullable=False)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'app_uuid': self.app_uuid.hex,
            'user_uuid': self.user_uuid.hex,
            'question_uuid': self.question_id.hex,
            'question_option_uuid': self.question_option_id.hex,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
        }


class QuestionOption(Base, UUIDMixin):
    __tablename__ = 'question_options'

    # Validation
    title_length = 255
    short_name_length = 255

    title = Column(Unicode(255), nullable=True)
    short_name = Column(Unicode(255), nullable=True)
    responses_count = Column(Integer(), default=0)
    question_id = Column(
        UUIDType(binary=False), ForeignKey('questions.uuid'), nullable=False)
    responses = relationship(
        QuestionResponse, backref='question_options', lazy="dynamic")
    question = relationship("Question", backref="questions")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'short_name': self.short_name,
            'responses_count': self.responses_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Question(Base, UUIDMixin):
    __tablename__ = 'questions'

    # Validation
    question_types = (
        'free_text',
        'multiple_choice',
    )
    content_types = (
        'page',
        'category',
        'localisation',
    )
    title_length = 255
    short_name_length = 255

    title = Column(Unicode(255), nullable=False)
    short_name = Column(Unicode(255), nullable=True)
    multiple = Column(Boolean(255), default=True)
    numeric = Column(Boolean(255), default=False)
    question_type = Column(Unicode(255), nullable=False)
    content_type = Column(Unicode(255), nullable=False)
    locale = Column(Unicode(6), nullable=False)
    options = relationship(QuestionOption, backref='questions', lazy="dynamic")
    responses = relationship(
        QuestionResponse, backref='questions', lazy="dynamic")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now())

    author_uuid = Column(UUIDType(binary=False), nullable=False)
    app_uuid = Column(UUIDType(binary=False), nullable=False)
    content_uuid = Column(UUIDType(binary=False), nullable=False)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'author_uuid': self.author_uuid.hex,
            'app_uuid': self.app_uuid.hex,
            'content_uuid': self.content_uuid.hex,
            'title': self.title,
            'short_name': self.short_name,
            'multiple': self.multiple,
            'numeric': self.numeric,
            'question_type': self.question_type,
            'locale': self.locale,
            'options': [option.to_dict() for option in self.options],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
