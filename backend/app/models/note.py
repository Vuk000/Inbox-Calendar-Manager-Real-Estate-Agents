"""Note model for polymorphic note-taking on various entities"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class Note(Base):
    """Polymorphic notes that can be attached to contacts, properties, or transactions"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Author
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Polymorphic associations (nullable to support multiple entity types)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, index=True)
    
    # Note content
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    
    # Metadata
    is_pinned = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)  # Private to creator, not shared with team
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notes")
    contact = relationship("Contact", back_populates="notes_list")
    property = relationship("Property", back_populates="notes_list")
    transaction = relationship("Transaction", back_populates="notes_list")
    
    def __repr__(self):
        entity = "contact" if self.contact_id else "property" if self.property_id else "transaction"
        return f"<Note(id={self.id}, {entity}_id={getattr(self, f'{entity}_id')})>"

