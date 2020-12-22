const setToken = function(nominationId, token) {
    document.querySelector(`#form-${nominationId}`).innerHTML = `<code>${token}</code>`;
}

window.onload = function() {
    for (const btn of document.querySelectorAll('.token-button')) {
        const nominationId = btn.dataset.nominationId;

        const token = localStorage.getItem(`token-${nominationId}`);
        if (token) {
            setToken(nominationId, token);
        } else {
            btn.type = 'button';
            btn.addEventListener('click', function() {
                fetch(`/token/${nominationId}/plain`)
                    .then(resp => {
                        if (resp.status !== 200) {
                            throw Error("Server responded with status code " + resp.status)
                        }
                        return resp.text();
                    })
                    .then(token => {
                        localStorage.setItem(`token-${nominationId}`, token);
                        setToken(nominationId, token);
                    })
                    .catch(reason => alert('Error!\n\n' + reason));
            });
        }
    }
};
