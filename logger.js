const { createLogger, format, transports } = require('winston');
const { combine, timestamp, printf } = format;

const logFormat = printf(({ level, message, timestamp }) => {
  return `${timestamp} [${level}]: ${message}`;
});

const logger = createLogger({
  level: 'info',
  format: combine(
    format((info) => {
      info.timestamp = Date.now();
      return info;
    })(),
    logFormat
  ),
  transports: [
    new transports.File({ filename: 'app.log' })
  ]
});

function addConsoleTransport(logger) {
  logger.add(new transports.Console());
}

function logInfo(isConsole, ...message) {
    if (isConsole) {
        console.log(message);
    }
}
module.exports = { logger, addConsoleTransport, logInfo};