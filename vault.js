// vault.js
const nacl = require('tweetnacl');
nacl.util = require('tweetnacl-util');

const MASTER_KEY = process.env.MASTER_KEY;
if(!MASTER_KEY) throw new Error("MASTER_KEY missing in env");

function keyFromMaster() {
  // derive 32-byte key (simple hash)
  const encoder = new TextEncoder();
  const data = encoder.encode(MASTER_KEY);
  // simple SHA-256
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(data).digest();
}

function encrypt(text){
  const key = keyFromMaster();
  const nonce = cryptoRandomBytes(24);
  const msg = Buffer.from(text, 'utf8');
  const boxed = require('tweetnacl').secretbox(new Uint8Array(msg), nonce, key);
  return Buffer.concat([Buffer.from(nonce), Buffer.from(boxed)]).toString('base64');
}

function decrypt(b64){
  const buf = Buffer.from(b64, 'base64');
  const nonce = buf.slice(0,24);
  const boxed = buf.slice(24);
  const key = keyFromMaster();
  const msg = require('tweetnacl').secretbox.open(new Uint8Array(boxed), nonce, key);
  if(!msg) throw new Error('Decryption failed');
  return Buffer.from(msg).toString('utf8');
}

function cryptoRandomBytes(n){
  const crypto = require('crypto');
  return crypto.randomBytes(n);
}

module.exports = { encrypt, decrypt };
