# veilleur

A Python script using instaloader to monitor Instagram accounts for lost followees or followers. Optionally sends
SMS notifications via Twilio. Best suited with a daily cron job.

## Features

- Reuses session whenever possible to avoid unnecessary logins.
- Supports 2FA authentication via command prompt arguments.
- Sends SMS notifications for lost followees or followers.
- Configurable through environment variables.

## Usage

> Python version is 3.14.2

### Setup

```sh
pipenv install
```

### Script

```sh
python -m src.main <opt: two_factor_code>
```

### Tests

```sh
python -m pytest
```

## Disclaimer

This is for educational purposes only. I am not responsible for any damage caused by this tool.

## License

GPLv3 © dxxxxy