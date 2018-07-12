#!/usr/bin/env node

"use strict";
const baseAbsPath = __dirname + '/';
const Promise = require('bluebird');
const util = require('util');
const Logger = require('./utils/Logger');
const logger = Logger.instance.getLogger(__filename);

const { spawn, exec } = require('child_process');

const fs = require('fs');
const path = require('path');

const packageInfo = JSON.parse(fs.readFileSync(baseAbsPath + 'package.json', 'utf8'));
let childProcesses = [];

const ArgumentParser = require('argparse').ArgumentParser;
const parser = new ArgumentParser({
  version: packageInfo.version,
  addHelp: true,
  description: packageInfo.description,
});
parser.addArgument(
  ['--totalUsers'],
  {
    defaultValue: null,
    required: true,
    help: 'The expected number of \"concurrent total users\" to maintain during stressing.'
  }
);
parser.addArgument(
  ['--hatchRate'],
  {
    defaultValue: null,
    required: false,
    help: 'The rate to hatch \"concurrent total users\" to the expected value. By default it equals to `--totalUsers`.'
  }
);
parser.addArgument(
  ['--numReqs'],
  {
    defaultValue: null,
    required: false,
    help: 'The total number of requests to perform for this sprint/stressing.'
  }
);
parser.addArgument(
  ['--locustFile'],
  {
    defaultValue: null,
    required: true,
    help: 'The relative/absolute path of the task definition file.'
  }
);
parser.addArgument(
  ['--csvDirPath'],
  {
    defaultValue: null,
    required: true,
    help: 'The relative/absolute path of the directory to save generated csv reports.'
  }
);

const args = parser.parseArgs();
const dateDesiredPattern = new Date().toISOString();

const dirStat = fs.statSync(args.csvDirPath);
if (!dirStat.isDirectory()) {
  logger.error("Please create the directory %s first.", args.csvDirPath);
}

const csvDirPathWithSlash = (/\/$/.test(args.csvPathPattern) ? args.csvDirPath : (args.csvPath + "/"));
const csvPathPattern = csvDirPathWithSlash + path.basename(args.locustFile, '.py') + "_" + args.totalUsers + "_" + dateDesiredPattern;
const hatchRate = (null == args.hatchRate ? args.totalUsers : args.hatchRate);

const cmd = util.format('locust');
const cmdArgs = (
                  null == args.numReqs
                  ?
                  ['-f', args.locustFile, '--no-web', '-c', args.totalUsers, '-r', hatchRate, '--csv', csvPathPattern]
                  :
                  ['-f', args.locustFile, '--no-web', '-c', args.totalUsers, '-r', hatchRate, '-n', args.numReqs, '--csv', csvPathPattern]
                ); 

const cp = spawn(cmd, cmdArgs, {
  stdio: 'inherit'
}); 
logger.info(util.format("Started child process pid == %s.", cp.pid));
childProcesses.push(cp);

function handleExit(signalOrCode) {
  logger.info(`Received signal or code ${signalOrCode}`);
  for (let cp of childProcesses) {
    logger.warn(util.format("Killing child process pid == %s.", cp.pid));
    cp.kill();
  }
}

process.on('SIGINT', handleExit);
process.on('SIGTERM', handleExit);
process.on('exit', handleExit);
