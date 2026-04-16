from src.main import compute_lost
from src.utils import format_message, save, load, send_sms


def test_compute_lost_bigger_prev():
    prev = {"user1", "user2", "user3"}
    curr = {"user2", "user3"}

    assert compute_lost(prev, curr) == {"user1"}


def test_compute_lost_equal():
    prev = {"user1", "user2"}
    curr = {"user1", "user2"}

    assert compute_lost(prev, curr) == set()


def test_compute_lost_bigger_curr():
    prev = {"user1", "user2"}
    curr = {"user1", "user2", "user3"}

    assert compute_lost(prev, curr) == set()


def test_compute_lost_empty_curr():
    prev = {"user1", "user2"}
    curr = set()

    assert compute_lost(prev, curr) == {"user1", "user2"}


def test_compute_lost_both_empty():
    prev = set()
    curr = set()

    assert compute_lost(prev, curr) == set()


def test_compute_lost_empty_prev():
    prev = set()
    curr = {"user1", "user2"}

    assert compute_lost(prev, curr) == set()


def test_format_message_lost_both():
    lost_followers = {"user1", "user2"}
    lost_followees = {"user3"}

    assert "Lost Followers:" in format_message(lost_followers, lost_followees)
    assert "Lost Followees:" in format_message(lost_followers, lost_followees)

    assert "user1" in format_message(lost_followers, lost_followees)
    assert "user2" in format_message(lost_followers, lost_followees)
    assert "user3" in format_message(lost_followers, lost_followees)


def test_format_message_lost_followers():
    lost_followers = {"user1", "user2"}
    lost_followees = set()

    assert "Lost Followers:" in format_message(lost_followers, lost_followees)
    assert "Lost Followees:" not in format_message(lost_followers, lost_followees)

    assert "user1" in format_message(lost_followers, lost_followees)
    assert "user2" in format_message(lost_followers, lost_followees)


def test_format_message_lost_followees():
    lost_followers = set()
    lost_followees = {"user3"}

    assert "Lost Followers:" not in format_message(lost_followers, lost_followees)
    assert "Lost Followees:" in format_message(lost_followers, lost_followees)

    assert "user3" in format_message(lost_followers, lost_followees)


def test_save_and_load(tmp_path):
    path = tmp_path / "test.json"
    content = {"user1", "user2", "user3"}

    save(path, content)
    loaded_content = set(load(path))

    assert loaded_content == content


def test_load_nonexistent_file(tmp_path):
    path = tmp_path / "nonexistent.json"

    loaded_content = load(path)

    assert loaded_content is None


def test_send_sms(mocker):
    mock_client = mocker.Mock()
    mock_messages = mocker.Mock()
    mock_client.messages = mock_messages
    mocker.patch("src.utils.Client", return_value=mock_client)
    mocker.patch("os.getenv", return_value="valid")

    result = send_sms("hello")

    assert result is True
    mock_messages.create.assert_called_once()


def test_send_sms_missing_env(mocker):
    mocker.patch("os.getenv", return_value=None)

    result = send_sms("hello")

    assert result is False
