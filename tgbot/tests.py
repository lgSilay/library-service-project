import unittest
from unittest.mock import patch

import requests
import asynctest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, Chat
from tgbot.routers.info_router import command_help_handler

from tgbot.notificatior import send_notification
from tgbot.routers.login_router import command_login, Form


class TestSendNotification(unittest.TestCase):
    def setUp(self):
        self.receivers = [123456789, 987654321]
        self.notification = "Test notification"

    @patch("tgbot.notificatior.requests.get")
    @patch("tgbot.notificatior.os.environ.get")
    def test_successful_notification(self, mock_get, mock_request_get):
        mock_get.return_value = "test_token"
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.raise_for_status.return_value = None

        send_notification(self.receivers, self.notification)

        self.assertEqual(mock_request_get.call_count, len(self.receivers))

    @patch("tgbot.notificatior.os.environ.get")
    def test_missing_token(self, mock_get):
        mock_get.return_value = None

        self.assertEqual(
            send_notification(self.receivers, self.notification),
            self.receivers,
        )

    @patch("tgbot.notificatior.requests.get")
    @patch("tgbot.notificatior.os.environ.get")
    def test_failed_notification(self, mock_get, mock_request_get):
        mock_get.return_value = "test_token"
        mock_request_get.return_value.status_code = 400
        mock_request_get.return_value.raise_for_status.side_effect = (
            requests.HTTPError
        )

        self.assertEqual(
            send_notification(self.receivers, self.notification),
            self.receivers,
        )


class TestBotHandlers(asynctest.TestCase):
    async def test_command_help_handler(self):
        message = asynctest.Mock(spec=Message)
        message.from_user = User(id=123, first_name="Test", is_bot=False)
        message.chat = Chat(id=456, type="private")
        message.text = "/help"

        message.answer = asynctest.CoroutineMock()

        await command_help_handler(message)

        message.answer.assert_called_once_with(
            "It is a bot where you can receive notifications.\n"
            "Please, use /login to attach your website profile."
        )

    async def test_command_start_attached_to_handler(self):
        message = asynctest.Mock(spec=Message)
        message.from_user = User(id=123, first_name="Test", is_bot=False)
        message.chat = Chat(id=456, type="private")
        message.text = "/start"

        message.answer = asynctest.CoroutineMock()

        await command_help_handler(message)

        message.answer.assert_called_once_with(
            "It is a bot where you can receive notifications.\n"
            "Please, use /login to attach your website profile."
        )

    async def test_command_login_called(self):
        message = asynctest.Mock(spec=Message)
        message.answer = asynctest.CoroutineMock()
        message.chat = Chat(id=456, type="private")

        state = asynctest.MagicMock(spec=FSMContext)

        await command_login(message, state)

        state.set_state.assert_called_once_with(Form.email)
        message.answer.assert_called_once_with("Enter your email:")
