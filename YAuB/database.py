"""CRUD definitions for SQLAlchemy objects"""

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, MetaData

db = SQLAlchemy()
metadata = MetaData()


class _Base(db.Model):
    __abstract__ = True
    rowid = Column(Integer, primary_key=True)

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""

        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()
