"""
Performance Tests for Timeline Endpoint
Target: <500ms response time with 1000 communications
"""
import pytest
import time
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from app.services.contact_service import ContactService


@pytest.fixture
def test_user_with_large_timeline(db: Session):
    """Create user with contact that has 1000 communications"""
    # Create user
    user = User(
        email="perf_test@example.com",
        hashed_password="hashed",
        full_name="Performance Test User"
    )
    db.add(user)
    db.commit()
    
    # Create contact
    contact = Contact(
        user_id=user.id,
        first_name="High",
        last_name="Volume",
        email="highvolume@example.com"
    )
    db.add(contact)
    db.commit()
    
    # Create 1000 communication logs
    communications = []
    now = datetime.utcnow()
    
    for i in range(1000):
        comm = CommunicationLog(
            user_id=user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL if i % 3 == 0 else CommunicationType.SMS,
            direction=CommunicationDirection.INBOUND if i % 2 == 0 else CommunicationDirection.OUTBOUND,
            subject=f"Communication {i}" if i % 3 == 0 else None,
            body=f"Body content for communication {i}",
            occurred_at=now - timedelta(hours=i),
            sentiment_score=(i % 10) / 10.0 - 0.5,  # Range from -0.5 to 0.4
            urgency_score=float(i % 100)
        )
        communications.append(comm)
    
    db.bulk_save_objects(communications)
    db.commit()
    
    return user, contact


@pytest.mark.performance
class TestTimelinePerformance:
    """Performance tests for timeline endpoint"""
    
    def test_timeline_loads_under_500ms(self, db: Session, test_user_with_large_timeline):
        """Timeline with 1000 communications should load in <500ms"""
        user, contact = test_user_with_large_timeline
        
        # Warm up database connections
        ContactService.get_contact_timeline(db, contact.id, user.id, limit=10)
        
        # Actual performance test
        start_time = time.time()
        
        timeline = ContactService.get_contact_timeline(
            db=db,
            contact_id=contact.id,
            user_id=user.id,
            limit=50  # Default limit
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Assertions
        assert len(timeline) == 50  # Should return limited results
        assert elapsed_ms < 500, f"Timeline took {elapsed_ms:.2f}ms, should be <500ms"
        
        # Verify data is sorted correctly
        for i in range(len(timeline) - 1):
            assert timeline[i].occurred_at >= timeline[i+1].occurred_at, "Timeline not sorted correctly"
    
    def test_timeline_with_full_limit(self, db: Session, test_user_with_large_timeline):
        """Timeline with max limit (200) should still be performant"""
        user, contact = test_user_with_large_timeline
        
        start_time = time.time()
        
        timeline = ContactService.get_contact_timeline(
            db=db,
            contact_id=contact.id,
            user_id=user.id,
            limit=200
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert len(timeline) == 200
        assert elapsed_ms < 1000, f"Large timeline took {elapsed_ms:.2f}ms, should be <1000ms"
    
    def test_timeline_query_optimization(self, db: Session, test_user_with_large_timeline):
        """Verify timeline uses efficient database queries"""
        user, contact = test_user_with_large_timeline
        
        # Enable query logging
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        
        queries = []
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            queries.append(statement)
        
        # Execute timeline query
        ContactService.get_contact_timeline(
            db=db,
            contact_id=contact.id,
            user_id=user.id,
            limit=50
        )
        
        # Should use minimal queries (ideally 1 for timeline)
        # Filter out transaction/session management queries
        timeline_queries = [q for q in queries if 'communication_logs' in q.lower()]
        
        assert len(timeline_queries) <= 2, f"Too many queries: {len(timeline_queries)}"
        
        # Check for LIMIT clause (query optimization)
        assert any('LIMIT' in q for q in timeline_queries), "Query should use LIMIT"


@pytest.mark.performance
class TestDatabaseIndexing:
    """Verify database indexes exist for performance"""
    
    def test_communication_logs_has_contact_index(self, db: Session):
        """Verify index on communication_logs.contact_id"""
        from sqlalchemy import inspect
        
        inspector = inspect(db.bind)
        indexes = inspector.get_indexes('communication_logs')
        
        # Find index on contact_id
        contact_id_indexed = any(
            'contact_id' in idx['column_names']
            for idx in indexes
        )
        
        assert contact_id_indexed, "Missing index on communication_logs.contact_id"
    
    def test_communication_logs_has_occurred_at_index(self, db: Session):
        """Verify index on communication_logs.occurred_at"""
        from sqlalchemy import inspect
        
        inspector = inspect(db.bind)
        indexes = inspector.get_indexes('communication_logs')
        
        # Find index on occurred_at
        occurred_at_indexed = any(
            'occurred_at' in idx['column_names']
            for idx in indexes
        )
        
        assert occurred_at_indexed, "Missing index on communication_logs.occurred_at"
    
    def test_communication_logs_has_composite_index(self, db: Session):
        """Verify composite index on (contact_id, occurred_at)"""
        from sqlalchemy import inspect
        
        inspector = inspect(db.bind)
        indexes = inspector.get_indexes('communication_logs')
        
        # Find composite index
        composite_indexed = any(
            'contact_id' in idx['column_names'] and 'occurred_at' in idx['column_names']
            for idx in indexes
        )
        
        assert composite_indexed, "Missing composite index on (contact_id, occurred_at)"


@pytest.mark.performance
@pytest.mark.slow
class TestScalabilityLimits:
    """Test system behavior at scale limits"""
    
    def test_handles_contact_with_10k_communications(self, db: Session):
        """Verify system can handle extreme case: 10K communications per contact"""
        # Create user and contact
        user = User(email="extreme@example.com", hashed_password="hashed", full_name="Extreme User")
        db.add(user)
        db.commit()
        
        contact = Contact(user_id=user.id, first_name="Extreme", email="extreme@example.com")
        db.add(contact)
        db.commit()
        
        # Bulk create 10K communications
        now = datetime.utcnow()
        communications = []
        
        for i in range(10000):
            communications.append(
                CommunicationLog(
                    user_id=user.id,
                    contact_id=contact.id,
                    communication_type=CommunicationType.EMAIL,
                    direction=CommunicationDirection.INBOUND,
                    occurred_at=now - timedelta(hours=i),
                    body=f"Message {i}"
                )
            )
        
        # Batch insert for performance
        db.bulk_save_objects(communications)
        db.commit()
        
        # Query should still work (with limit)
        start_time = time.time()
        timeline = ContactService.get_contact_timeline(db, contact.id, user.id, limit=50)
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert len(timeline) == 50
        assert elapsed_ms < 1000, f"Extreme case took {elapsed_ms:.2f}ms"

