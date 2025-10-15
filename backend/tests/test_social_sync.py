import pytest
from datetime import datetime
from unittest.mock import patch

from app.models.social_account import SocialAccount, SocialProvider
from app.models.message import Message, MessageSource
from app.workers.social_sync import sync_twitter_account, sync_facebook_account


@pytest.fixture
def twitter_account(db, test_user):
  account = SocialAccount(
      user_id=test_user.id,
      provider=SocialProvider.TWITTER,
      handle='agent_realinbox',
      display_name='Agent RealInbox',
      encrypted_access_token='encrypted-token',
      encrypted_refresh_token='encrypted-refresh',
      is_active=True
  )
  db.add(account)
  db.commit()
  db.refresh(account)
  return account


@pytest.fixture
def facebook_account(db, test_user):
  account = SocialAccount(
      user_id=test_user.id,
      provider=SocialProvider.FACEBOOK_MESSENGER,
      handle='RealInbox Realty',
      display_name='RealInbox Realty',
      encrypted_access_token='encrypted-page-token',
      page_id='123456789',
      is_active=True
  )
  db.add(account)
  db.commit()
  db.refresh(account)
  return account


@patch('app.integrations.twitter_integration.TwitterIntegration.list_direct_messages')
@patch('app.integrations.twitter_integration.TwitterIntegration.normalize_dm_event')
def test_sync_twitter_account_creates_messages(mock_normalize, mock_list, db, twitter_account):
  mock_list.return_value = {
      'data': [
          {'event': {'id': '1', 'message_create': {'sender_id': 'buyer', 'target': {'recipient_id': 'agent'}, 'message_data': {'text': 'Hi!'}}}}
      ]
  }
  mock_normalize.return_value = {
      'external_id': '1',
      'sender_id': 'buyer',
      'recipient_id': 'agent',
      'text': 'Hi!',
      'sent_at': datetime.utcnow().timestamp() * 1000
  }

  result = sync_twitter_account.apply(args=(twitter_account.id,), kwargs={'db': db}).get()

  assert result['status'] == 'success'
  message = db.query(Message).filter(Message.social_account_id == twitter_account.id).first()
  assert message is not None
  assert message.source == MessageSource.TWITTER_DM
  assert message.sender_email == 'buyer'


@patch('app.integrations.facebook_messenger.FacebookMessengerIntegration.get_conversations')
@patch('app.integrations.facebook_messenger.FacebookMessengerIntegration.normalize_message')
def test_sync_facebook_account_creates_messages(mock_normalize, mock_get, db, facebook_account):
  mock_get.return_value = {
      'data': [
          {
              'messages': {
                  'data': [
                      {
                          'id': 'mid-1',
                          'from': {'id': 'buyer'},
                          'to': {'data': [{'id': 'page'}]},
                          'message': 'Interested in the property',
                          'created_time': '2025-10-14T10:00:00Z'
                      }
                  ]
              }
          }
      ]
  }
  mock_normalize.return_value = {
      'mid': 'mid-1',
      'sender_id': 'buyer',
      'recipient_id': 'page',
      'text': 'Interested in the property'
  }

  result = sync_facebook_account.apply(args=(facebook_account.id,), kwargs={'db': db}).get()

  assert result['status'] == 'success'
  message = db.query(Message).filter(Message.social_account_id == facebook_account.id).first()
  assert message is not None
  assert message.source == MessageSource.FACEBOOK_MESSENGER
  assert message.sender_email == 'buyer'
