/* Careers application form — gathers the fields and posts them as JSON to /api/careers,
   which emails the team and sends the applicant a confirmation. Progressive enhancement:
   the form still works as a normal POST if JS is off (the function accepts form-encoded too). */
(function () {
  var form = document.getElementById('careers-form');
  if (!form) return;
  var status = form.querySelector('[data-careers-status]');

  function setStatus(text, ok) {
    if (!status) return;
    status.textContent = text;
    status.className = 'mt-3 text-sm text-center mb-0 ' +
      (ok === true ? 'text-green font-semibold' : ok === false ? 'text-orange font-semibold' : 'text-darkgrey');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.company && form.company.value) return;          // honeypot
    if (!form.checkValidity()) { form.reportValidity(); return; }

    var fd = new FormData(form), data = {};
    fd.forEach(function (v, k) {
      if (k === 'company') return;
      if (k === 'licenceCats') { (data.licenceCats = data.licenceCats || []).push(v); }
      else data[k] = v;
    });

    var btn = form.querySelector('[type=submit]');
    btn.disabled = true;
    setStatus('Sending your application…');

    fetch('/api/careers', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data)
    }).then(function (r) {
      return r.json().then(function (d) { return { ok: r.ok, d: d }; }).catch(function () { return { ok: r.ok, d: {} }; });
    }).then(function (res) {
      if (res.ok && res.d && res.d.ok) {
        form.reset();
        setStatus('Thank you! Your application has been sent and a copy is on its way to your email. We’ll be in touch.', true);
      } else {
        setStatus((res.d && res.d.error) || 'Sorry, we couldn’t send your application just now — please email your CV to us instead.', false);
        btn.disabled = false;
      }
    }).catch(function () {
      setStatus('Sorry, we couldn’t send your application just now — please email your CV to us instead.', false);
      btn.disabled = false;
    });
  });
})();
