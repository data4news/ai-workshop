// steps.js
// Step-by-step sections built from <details class="step">: only one is open at
// a time, and each "Next" button (.next-step[data-next="step-id"]) opens the
// following step. The shared `name` on the <details> handles one-at-a-time in
// newer browsers; the toggle handler covers older ones.

(function () {
    const steps = document.querySelectorAll('details.step');

    steps.forEach(step => step.addEventListener('toggle', () => {
        if (step.open) steps.forEach(other => { if (other !== step) other.open = false; });
    }));

    document.querySelectorAll('.next-step').forEach(button => button.addEventListener('click', () => {
        const next = document.getElementById(button.dataset.next);
        next.open = true;
        next.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
})();
