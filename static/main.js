/*   1. The Password Eye Toggle */
function toggleEye(inputId, btnId) {
    var passField = document.getElementById(inputId);
    var btn = document.getElementById(btnId);

    if (passField.type === "password") {
        passField.type = "text";
        btn.innerHTML = "🔓"; // Unlocked!
    } else {
        passField.type = "password";
        btn.innerHTML = "🔒"; // Locked!
    }
}

/*    2. Live Password Strength Checker */
function checkPasswordStrength() {
    // Get whatever the user just typed into the password box
    var password = document.getElementById("passInput").value;

    // Find the checklist items on the screen
    var lengthCheck = document.getElementById("check-length");
    var upperCheck = document.getElementById("check-upper");
    var numberCheck = document.getElementById("check-number");

    // Rule 1: Is it 8 or more characters?
    if (password.length >= 8) {
        lengthCheck.style.color = "green";
        lengthCheck.innerHTML = "✔ 8+ characters";
    } else {
        lengthCheck.style.color = "red";
        lengthCheck.innerHTML = "❌ 8+ characters";
    }

    // Rule 2: Does it have an uppercase letter? (Using a simple pattern match)
    if (/[A-Z]/.test(password)) {
        upperCheck.style.color = "green";
        upperCheck.innerHTML = "✔ One uppercase";
    } else {
        upperCheck.style.color = "red";
        upperCheck.innerHTML = "❌ One uppercase";
    }

    // Rule 3: Does it have a number?
    if (/[0-9]/.test(password)) {
        numberCheck.style.color = "green";
        numberCheck.innerHTML = "✔ One number";
    } else {
        numberCheck.style.color = "red";
        numberCheck.innerHTML = "❌ One number";
    }
}
