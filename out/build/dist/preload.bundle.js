(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
const { ipcRenderer } = require('electron')
const jsonStringify = require('@bugsnag/safe-json-stringify')
const { CHANNEL_RENDERER_TO_MAIN, CHANNEL_RENDERER_TO_MAIN_SYNC } = require('./lib/constants')

const safeInvoke = (runSynchronous, method, ...args) => {
  const bridge = runSynchronous ? 'sendSync' : 'invoke'
  const channel = runSynchronous ? CHANNEL_RENDERER_TO_MAIN_SYNC : CHANNEL_RENDERER_TO_MAIN
  return ipcRenderer[bridge](channel, method, ...args.map(arg => jsonStringify(arg)))
}

const BugsnagIpcRenderer = {
  // these static values are populated by preload.js
  config: null,
  process: null,

  update ({ context, user, metadata, features }) {
    return safeInvoke(false, 'update', { context, user, metadata, features })
  },

  getContext () {
    return safeInvoke(true, 'getContext')
  },

  setContext (context) {
    return safeInvoke(false, 'setContext', context)
  },

  addMetadata (...args) {
    return safeInvoke(false, 'addMetadata', ...args)
  },

  clearMetadata (...args) {
    return safeInvoke(false, 'clearMetadata', ...args)
  },

  getMetadata (...args) {
    return safeInvoke(true, 'getMetadata', ...args)
  },

  addFeatureFlag (...args) {
    return safeInvoke(false, 'addFeatureFlag', ...args)
  },

  addFeatureFlags (...args) {
    return safeInvoke(false, 'addFeatureFlags', ...args)
  },

  clearFeatureFlag (...args) {
    return safeInvoke(false, 'clearFeatureFlag', ...args)
  },

  clearFeatureFlags () {
    return safeInvoke(false, 'clearFeatureFlags')
  },

  getUser () {
    return safeInvoke(true, 'getUser')
  },

  setUser (...args) {
    return safeInvoke(false, 'setUser', ...args)
  },

  leaveBreadcrumb (...args) {
    return safeInvoke(false, 'leaveBreadcrumb', ...args)
  },

  startSession () {
    return safeInvoke(false, 'startSession')
  },

  pauseSession () {
    return safeInvoke(false, 'pauseSession')
  },

  resumeSession () {
    return safeInvoke(false, 'resumeSession')
  },

  dispatch (event) {
    return safeInvoke(false, 'dispatch', event)
  },

  getPayloadInfo () {
    return safeInvoke(false, 'getPayloadInfo')
  }
}

module.exports = BugsnagIpcRenderer

},{"./lib/constants":2,"@bugsnag/safe-json-stringify":3,"electron":undefined}],2:[function(require,module,exports){
module.exports.CHANNEL_CONFIG = 'bugsnag::configure'
module.exports.CHANNEL_RENDERER_TO_MAIN_SYNC = 'bugsnag::renderer-to-main-sync'
module.exports.CHANNEL_RENDERER_TO_MAIN = 'bugsnag::renderer-to-main'

},{}],3:[function(require,module,exports){
module.exports = function (data, replacer, space, opts) {
  var redactedKeys = opts && opts.redactedKeys ? opts.redactedKeys : []
  var redactedPaths = opts && opts.redactedPaths ? opts.redactedPaths : []
  return JSON.stringify(
    prepareObjForSerialization(data, redactedKeys, redactedPaths),
    replacer,
    space
  )
}

var MAX_DEPTH = 20
var MAX_EDGES = 25000
var MIN_PRESERVED_DEPTH = 8

var REPLACEMENT_NODE = '...'

function isError (o) {
  return o instanceof Error ||
    /^\[object (Error|(Dom)?Exception)\]$/.test(Object.prototype.toString.call(o))
}

function throwsMessage (err) {
  return '[Throws: ' + (err ? err.message : '?') + ']'
}

function find (haystack, needle) {
  for (var i = 0, len = haystack.length; i < len; i++) {
    if (haystack[i] === needle) return true
  }
  return false
}

// returns true if the string `path` starts with any of the provided `paths`
function isDescendent (paths, path) {
  for (var i = 0, len = paths.length; i < len; i++) {
    if (path.indexOf(paths[i]) === 0) return true
  }
  return false
}

function shouldRedact (patterns, key) {
  for (var i = 0, len = patterns.length; i < len; i++) {
    if (typeof patterns[i] === 'string' && patterns[i].toLowerCase() === key.toLowerCase()) return true
    if (patterns[i] && typeof patterns[i].test === 'function' && patterns[i].test(key)) return true
  }
  return false
}

function isArray (obj) {
  return Object.prototype.toString.call(obj) === '[object Array]'
}

function safelyGetProp (obj, prop) {
  try {
    return obj[prop]
  } catch (err) {
    return throwsMessage(err)
  }
}

function prepareObjForSerialization (obj, redactedKeys, redactedPaths) {
  var seen = [] // store references to objects we have seen before
  var edges = 0

  function visit (obj, path) {
    function edgesExceeded () {
      return path.length > MIN_PRESERVED_DEPTH && edges > MAX_EDGES
    }

    edges++

    if (path.length > MAX_DEPTH) return REPLACEMENT_NODE
    if (edgesExceeded()) return REPLACEMENT_NODE
    if (obj === null || typeof obj !== 'object') return obj
    if (find(seen, obj)) return '[Circular]'

    seen.push(obj)

    if (typeof obj.toJSON === 'function') {
      try {
        // we're not going to count this as an edge because it
        // replaces the value of the currently visited object
        edges--
        var fResult = visit(obj.toJSON(), path)
        seen.pop()
        return fResult
      } catch (err) {
        return throwsMessage(err)
      }
    }

    var er = isError(obj)
    if (er) {
      edges--
      var eResult = visit({ name: obj.name, message: obj.message }, path)
      seen.pop()
      return eResult
    }

    if (isArray(obj)) {
      var aResult = []
      for (var i = 0, len = obj.length; i < len; i++) {
        if (edgesExceeded()) {
          aResult.push(REPLACEMENT_NODE)
          break
        }
        aResult.push(visit(obj[i], path.concat('[]')))
      }
      seen.pop()
      return aResult
    }

    var result = {}
    try {
      for (var prop in obj) {
        if (!Object.prototype.hasOwnProperty.call(obj, prop)) continue
        if (isDescendent(redactedPaths, path.join('.')) && shouldRedact(redactedKeys, prop)) {
          result[prop] = '[REDACTED]'
          continue
        }
        if (edgesExceeded()) {
          result[prop] = REPLACEMENT_NODE
          break
        }
        result[prop] = visit(safelyGetProp(obj, prop), path.concat(prop))
      }
    } catch (e) {}
    seen.pop()
    return result
  }

  return visit(obj, [])
}

},{}],4:[function(require,module,exports){
// preloads run in devtools panes too, but we don't want to run there
if (document.location.protocol === 'devtools:') return

const { ipcRenderer, contextBridge } = require('electron')
const BugsnagIpcRenderer = require('./bugsnag-ipc-renderer')
const { CHANNEL_CONFIG } = require('./lib/constants')

// one sync call is required on startup to get the main process config
const config = ipcRenderer.sendSync(CHANNEL_CONFIG)
if (!config) throw new Error('Bugsnag was not started in the main process before browser windows were created')

// attach config to the exposed interface
BugsnagIpcRenderer.config = JSON.parse(config)

// attach process info to the exposed interface
const { isMainFrame, sandboxed, type } = process
BugsnagIpcRenderer.process = { isMainFrame, sandboxed, type }

// expose Bugsnag as a global object for the browser
try {
  // assume contextIsolation=true
  contextBridge.exposeInMainWorld('__bugsnag_ipc__', BugsnagIpcRenderer)
} catch (e) {}

// expose for other preload scripts to use, this also covers contextIsolation=false
window.__bugsnag_ipc__ = BugsnagIpcRenderer

},{"./bugsnag-ipc-renderer":1,"./lib/constants":2,"electron":undefined}]},{},[4]);
