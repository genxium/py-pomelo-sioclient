const baseAbsPath = __dirname + '/';

const singleton = Symbol();
const singletonEnforcer = Symbol();

const bunyan = require('bunyan');
const PrettyStream = require('bunyan-prettystream');

const prettyStdOut = new PrettyStream();
prettyStdOut.pipe(process.stdout);

class Logger {
  static get instance() {
    if (!this[singleton]) {
      this[singleton] = new Logger(singletonEnforcer);
    }
    return this[singleton];
  }

  constructor(enforcer) {
    if (enforcer != singletonEnforcer) {
      throw "Cannot construct singleton";
    }
    const instance = this;
    instance.DEFAULT = 'default';
    this._defaultLogger = bunyan.createLogger({
      name: instance.DEFAULT,
      streams: [
        {
          level: 'info',
          stream: prettyStdOut
        }
      ]
    });
    this._loggerDict = {};
    this._loggerDict[this.DEFAULT] = this._defaultLogger;
  }

  getLogger(name) {
    const instance = this;
    if (undefined === name || null === name) {
      return instance._defaultLogger;
    }
    if (name in instance._loggerDict) {
      return instance._loggerDict[name];
    }
    return bunyan.createLogger({
      name: name,
      streams: [
        {
          level: 'info',
          stream: prettyStdOut
        }
      ]
    });
  }
}

module.exports = Logger;
