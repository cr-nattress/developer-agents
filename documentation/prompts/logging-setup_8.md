### Set up application-wide logging to a log directory

# Create a logging utility module called `logger.py` inside the `output/` directory.
- Configure Python's built-in `logging` module.
- Logs should be written to a file `app.log` inside a `log/` directory at the application root.
- Create the log directory if it doesn't exist.
- Log format should include timestamp, log level, and message.
- Include a function `get_logger(name: str)` that returns a preconfigured logger instance. 