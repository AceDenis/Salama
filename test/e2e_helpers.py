def fill_form(page, overrides=None, max_sections=20):
    overrides = overrides or {}
    for _ in range(max_sections):
        page.wait_for_selector("#wNext")
        # answer every visible unanswered radio group: first option, unless overridden
        page.evaluate("""(ov) => {
          document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => {
            const id = fs.dataset.id; const radios = [...fs.querySelectorAll('input[type=radio]')];
            if (!radios.length || radios.some(r => r.checked)) { if (!(id in ov)) return; }
            const want = id in ov ? String(ov[id]) : radios[0].value; const r = radios.find(x => x.value === want) || radios[0]; r.click();
          });
          Object.entries(ov).forEach(([k, v]) => { if (k.startsWith('chk_')) { const c = document.querySelector(`[data-check=${k.slice(4)}]`); if (c && !c.checked) c.click(); } });
          document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => { const id = fs.dataset.id; const radios=[...fs.querySelectorAll('input[type=radio]')]; if (radios.length && !radios.some(r=>r.checked)) radios[0].click(); });
        }""", overrides)
        page.wait_for_timeout(60)
        # repeat once: newly revealed gated items
        page.evaluate("""() => document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => { const radios=[...fs.querySelectorAll('input[type=radio]')]; if (radios.length && !radios.some(r=>r.checked)) radios[0].click(); })""")
        txt = page.inner_text("#wNext"); page.click("#wNext"); page.wait_for_timeout(120)
        if page.locator("#cont").count(): page.click("#cont"); page.wait_for_timeout(80)
        if txt.strip() in ("Finish", "Maliza"): return
    raise Exception("form did not finish")
