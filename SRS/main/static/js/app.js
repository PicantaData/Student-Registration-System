// Get references to the necessary HTML elements
const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const otpContainer = document.querySelector(".otp-container");
const emailContainer = document.querySelector(".input-field");
const passwordContainer = document.querySelector(".password-container");
const actionButton = document.querySelector("#actionButton");
const logInBtn = document.querySelector("#log-in-btn");
const signinEmailInput = document.querySelector("#signin-email");
const signupEmailInput = document.querySelector("#signup-email");
const otpInput = document.querySelector("#otp-input");
const passwordInput = document.querySelector("#password-input");
const confirmPasswordInput = document.querySelector("#confirm-password-input");

// Regular expression for validating email format
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Function to switch to the OTP mode
function switchToOTP() {
    container.classList.add("sign-up-mode");
    sign_up_btn.click();
}

// Event listener for the "Sign Up" button
sign_up_btn.addEventListener("click", () => {
    // Switch to the sign-up mode and show relevant elements
    container.classList.add("sign-up-mode");
    otpContainer.style.display = "block";
    passwordContainer.style.display = "block";
});

// ...

// Event listener for the "Action" button
actionButton.addEventListener('click', (event) => {
    // Get the values of the email, password, and confirm password inputs
    const emailValue = signupEmailInput.value;
    const passwordValue = passwordInput.value;
    const confirmPasswordValue = confirmPasswordInput.value;

    if (!emailRegex.test(emailValue)){
        alert("Please enter a correct email address.");
        event.preventDefault();
        return;
    }

    if (actionButton.textContent === 'Send OTP') {
        // Check if the passwords match
        if (passwordValue === confirmPasswordValue) {
            // Passwords match, activate the anchor event
            switchToOTP();
        } else {
            // Passwords don't match, prevent switching and show an alert
            alert("Passwords do not match!");
            event.preventDefault();
            return;
        }
    } else if (actionButton.textContent === 'Verify OTP') {
        // Handle the OTP verification logic here
        // For now, the code assumes OTP verification is successful
        otpInput.classList.add('d-none');
        passwordInput.classList.remove('d-none');
        confirmPasswordInput.classList.remove('d-none');
        emailContainer.style.display = "none";
        otpContainer.style.display = "block";
        passwordContainer.style.display = "none";
    }
});

// ...


// Event listener for the "Login" button
logInBtn.addEventListener("click", () => {
    // Determine the active email input based on the current mode
    const activeEmailInput = container.classList.contains("sign-up-mode") ? signupEmailInput : signinEmailInput;

    // Check if the entered email is valid
    if (!emailRegex.test(activeEmailInput.value)) {
        alert("Please enter a correct email address.");
        return;
    }
});

// Event listener for the "Sign In" button
sign_in_btn.addEventListener("click", () => {
    // Switch to the sign-in mode and reset the relevant elements
    container.classList.remove("sign-up-mode");
    otpContainer.style.display = "none";
    actionButton.textContent = "Send OTP";
});

// Function to simulate sending OTP (replace this with actual email sending logic)
function sendOTP(email) {
    // Simulate sending OTP via email
    alert(`OTP sent successfully on email: ${email}`);
}
