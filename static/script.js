//script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.onsubmit = function(event) {
        const password = form.querySelector('input[name=password1]').value;
        const password2 = form.querySelector('input[name=password2]').value;

        if (password !== password2) {
            alert("Passwords do not match.");
            event.preventDefault();
        }
    };
});
