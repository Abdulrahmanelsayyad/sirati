const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const assert = require('node:assert/strict');
const { test } = require('node:test');
const source = readFileSync(resolve(process.argv[2], 'app/builder/page.tsx'), 'utf8');
const start = source.indexOf('  function handlePhotoUpload(');
const end = source.indexOf('  function resetCv()', start);
assert(start >= 0 && end > start);
const handler = source.slice(start, end).replace('file?: File', 'file');
function upload(failure, language = 'en') {
  const alerts = [], operations = [];
  let data = { fullName: 'Synthetic', photoDataUrl: 'previous-photo' };
  const context = { fillStyle: '', fillRect() { operations.push(['fill', this.fillStyle]); },
    drawImage() { operations.push(['draw']); } };
  class Reader {
    readAsDataURL() {
      if (failure === 'read') this.onerror();
      else { this.result = 'synthetic-image'; this.onload(); }
    }
  }
  class Image {
    width = 720; height = 960;
    set src(value) { if (failure === 'decode') this.onerror(); else this.onload(); }
  }
  const canvas = { width: 0, height: 0,
    getContext: () => failure === 'context' ? null : context,
    toDataURL() { if (failure === 'encode') throw Error('Encoding failed'); return 'new-photo'; } };
  new Function('FileReader', 'Image', 'document', 'setData', 'alert', 'language',
    handler + "handlePhotoUpload({type:'image/png',size:100});")(
    Reader, Image, { createElement: () => canvas }, fn => data = fn(data),
    message => alerts.push(message), language);
  return { data, alerts, operations, canvas };
}
test('photo canvas paints white before compositing transparent pixels', () => {
  const result = upload();
  assert.deepEqual(result.operations, [['fill', '#ffffff'], ['draw']]);
  assert.equal(result.data.photoDataUrl, 'new-photo');
  assert.equal(result.data.fullName, 'Synthetic');
  assert.equal(result.canvas.width, 360);
  assert.equal(result.canvas.height, 480);
  assert.deepEqual(result.alerts, []);
});
for (const failure of ['read', 'decode', 'context', 'encode']) {
  test(`${failure} failure reports error and preserves previous photo`, () => {
    const result = upload(failure);
    assert.equal(result.data.photoDataUrl, 'previous-photo');
    assert.equal(result.alerts.length, 1);
    assert.match(result.alerts[0], /Could not open/);
  });
}
test('image failure message follows Arabic language', () => {
  assert.match(upload('decode', 'ar').alerts[0], /تعذر فتح الصورة/);
});
test('file input clears after selection so the same file can be retried', () => {
  const match = source.match(/accept="image\/\*" onChange=\{e => \{([^}]+)\}\}/);
  assert(match);
  const file = { name: 'portrait.png' }, target = { files: [file], value: 'portrait.png' };
  let selected;
  new Function('e', 'handlePhotoUpload', match[1])({ target }, f => selected = f);
  assert.equal(target.value, '');
  assert.equal(selected, file);
});
