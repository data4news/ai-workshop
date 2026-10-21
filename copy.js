// copy.js
// "Copy" buttons for code blocks: <div class="code-block"><button class="copy-button">
// copies the text of the <code> next to it.

(function () {
    document.querySelectorAll('.copy-button').forEach(button => button.addEventListener('click', () => {
        const code = button.parentElement.querySelector('code').innerText;
        navigator.clipboard.writeText(code).then(() => {
            button.textContent = 'Copied!';
            setTimeout(() => { button.textContent = 'Copy'; }, 1500);
        });
    }));
})();
