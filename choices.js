// choices.js
// The "I'm using ___ on ___" choice shared by every workshop page. It lives in
// the URL (?app=…&os=…), so it carries across pages through the sidebar links.
//
// On each page:
//   <select data-choice-group="app|os">  dropdowns kept in sync with the URL
//   body[data-app], body[data-os]       let CSS show the matching .app-* / .os-* steps
//   [data-fill="name|app|folder"]       filled with text for the chosen app
//   [data-needs="app os"]               shown once those choices are made
//   [data-prompt="app os"]              shown until they are

(function () {
    const apps = {
        deepseek: { name: 'DeepSeek Harness', app: 'DeepSeek Harness', folder: '.agents' },
        chatgpt: { name: 'ChatGPT', app: 'ChatGPT', folder: '.agents' },
        claude: { name: 'Claude Code', app: 'the Claude app', folder: '.claude' },
    };
    const choices = { app: Object.keys(apps), os: ['mac', 'windows', 'linux'] };

    const current = {};
    const params = new URLSearchParams(location.search);
    for (const [group, values] of Object.entries(choices)) {
        if (values.includes(params.get(group))) current[group] = params.get(group);
    }

    const selects = document.querySelectorAll('select[data-choice-group]');
    const isChosen = groups => groups.split(' ').every(group => current[group]);

    function apply() {
        for (const group of Object.keys(choices)) {
            if (current[group]) document.body.dataset[group] = current[group];
            else delete document.body.dataset[group];
        }
        selects.forEach(select => { select.value = current[select.dataset.choiceGroup] || ''; });

        const app = apps[current.app];
        if (app) {
            document.querySelectorAll('[data-fill]').forEach(el => { el.textContent = app[el.dataset.fill]; });
        }
        document.querySelectorAll('[data-needs]').forEach(el => { el.hidden = !isChosen(el.dataset.needs); });
        document.querySelectorAll('[data-prompt]').forEach(el => { el.hidden = isChosen(el.dataset.prompt); });

        // Keep the choice in this page's URL and in links to the other pages.
        const query = new URLSearchParams(current).toString();
        history.replaceState(null, '', query ? `?${query}${location.hash}` : location.pathname + location.hash);
        document.querySelectorAll('a[href]').forEach(link => {
            const href = link.getAttribute('href');
            if (link.dataset.baseHref === undefined) {
                if (/^([a-z]+:|\/|#)/i.test(href) || !/\.html(\?|$)/.test(href)) return;
                link.dataset.baseHref = href.split('?')[0];
            }
            link.setAttribute('href', query ? `${link.dataset.baseHref}?${query}` : link.dataset.baseHref);
        });
    }

    selects.forEach(select => select.addEventListener('change', () => {
        current[select.dataset.choiceGroup] = select.value;
        apply();
    }));
    apply();
})();
