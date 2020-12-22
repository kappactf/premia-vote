window.onload = function() {
    const error = document.querySelector(".alert-danger");
    const token = document.querySelector("#token");
    const savedToken = localStorage.getItem(`token-${window.nominationId}`);
    if (error === null && token !== null && savedToken !== null) {
        token.value = savedToken;
        document.querySelector("form").submit();
    }
}
