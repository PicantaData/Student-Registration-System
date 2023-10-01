const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const otpContainer = document.querySelector(".otp-container");
const sendOTPBtn = document.querySelector("#send-otp-btn");
const logInBtn = document.querySelector("#log-in-btn");
const signinEmailInput = document.querySelector("#signin-email");
const signupEmailInput = document.querySelector("#signup-email");
const otpInput = document.querySelector("#otp-input");
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Flag to track if the OTP button was clicked before
let otpButtonClicked = false;

sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
    // Initially hide OTP container
    otpContainer.style.display = "none";
    
    // If the OTP button was clicked before, change its text
    if (otpButtonClicked) {
        sendOTPBtn.textContent = "Submit Form";
    } else {
        sendOTPBtn.textContent = "Send OTP";
    }
});

sendOTPBtn.addEventListener("click", () => {
    // Determine the active email input based on the current mode
    const activeEmailInput = container.classList.contains("sign-up-mode") ? signupEmailInput : signinEmailInput;

    // Check if the entered email is valid
    if (!emailRegex.test(activeEmailInput.value)) {
        alert("Please enter a correct email-id.");
        return;
    }

    // Toggle OTP container visibility
    if(emailRegex.test(activeEmailInput.value)){
        if (otpContainer.style.display === "none" || otpContainer.style.display === "") {
              otpContainer.style.display = "block";
            sendOTPBtn.textContent = "Submit Form";
            // Set the flag to true when OTP button is clicked
            otpButtonClicked = true;

            // Simulate sending OTP (you can replace this with actual logic)
            sendOTP(activeEmailInput.value);
        } 
        else {
           otpContainer.style.display = "none";
           sendOTPBtn.textContent = "Send OTP";
       }
    }
});

logInBtn.addEventListener("click", () => {
     // Determine the active email input based on the current mode
     const activeEmailInput = container.classList.contains("sign-up-mode") ? signupEmailInput : signinEmailInput;

     // Check if the entered email is valid
     if (!emailRegex.test(activeEmailInput.value)) {
         alert("Please enter a correct email-id.");
         return;
     }
});

sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
    // Reset OTP container and button text when switching to Sign In
    otpContainer.style.display = "none";
    sendOTPBtn.textContent = "Send OTP";
    // Reset the flag when switching to Sign In
    otpButtonClicked = false;
});

// Function to simulate sending OTP (replace this with actual email sending logic)
function sendOTP(email) {
    // Simulate sending OTP via email
    alert(`OTP sent successfully on email: ${email}`);
}
