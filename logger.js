const { createLogger, format, transports } = require('winston');
const { printf, combine, splat } = format;

const logFormat = printf(({ level, message, timestamp, [Symbol.for('splat')]: splat }) => {
  // Initialize the return string with the timestamp, level, and message
  let return_string = `${timestamp} [${level}]: ${message}`;

  // Check if there are additional arguments (splat) and format them
  if (splat) {
    const additionalData = splat.map(data =>
      typeof data === 'object' ? JSON.stringify(data, null, 2) : data
    ).join(' ');
    return_string += ` ${additionalData}`;
  }

  return return_string;
});

const logger = createLogger({
  level: 'info',
  format: combine(
    // Add timestamp as a number
    format((info) => {
        info.timestamp = Date.now();
        return info;
      })(),

    splat(), // Handle multiple arguments passed to the logger
    logFormat // Use the custom log format
  ),
});

function addConsoleTransport(logger) {
  logger.add(new transports.Console());
}
function addFileTransport(logger, filename) {
  logger.add(new transports.File({ filename: filename }));
}

module.exports = { logger, addConsoleTransport, addFileTransport};