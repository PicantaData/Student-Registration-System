const personal_next_btn = document.querySelector("#personal_nextBtn");
const educational_next_btn = document.querySelector("#educational_nextBtn");
const educational_back_btn = document.querySelector("#educational_backBtn");
const payment_back_btn = document.querySelector("#payment_backBtn");
const payment_submit_btn = document.querySelector("#payment_submitBtn");
const container = document.querySelector(".container");
const container_personal = document.querySelector(".div-application-form-personal");
const container_educational = document.querySelector(".div-application-form-educational");
const container_payment = document.querySelector(".div-application-form-payment");
const container_sign_in = document.querySelector(".div-sign-in");
const countryCodeRegex = /^\+\d{1,3}$/;
const mobileRegex = /(\+\d{1,3}\s?)?((\(\d{3}\)\s?)|(\d{3})(\s|-?))(\d{3}(\s|-?))(\d{4})(\s?(([E|e]xt[:|.|]?)|x|X)(\s?\d+))?/;
const postalCodeRegex = /[a-z0-9][a-z0-9\- ]{0,10}[a-z0-9]/;
const resultRegex = /(\d{1,2}\.\d{1,2})/;

//Function to fetch and populate dropdown options
//  function populateDropdown(endpoint, dropdownId) {
//      const dropdown = document.getElementById(dropdownId);
//      dropdown.innerHTML = '<option value="">Select an option</option>'; // Clear existing options

//      fetch(endpoint)
//          .then((response) => response.json())
//          .then((data) => {
//              data.forEach((item) => {
//                  const option = document.createElement('option');
//                  option.value = item.id; // Use the appropriate field for value (e.g., 'id' or 'alpha2Code')
//                  option.textContent = item.name; // Use the appropriate field for name (e.g., 'name')
//                  dropdown.appendChild(option);
//              });
//          })
//          .catch((error) => {
//              console.error('Error fetching data:', error);
//          });
//  }

// // Event listeners for dropdowns
// const countryDropdown = document.querySelector("#country");
//  countryDropdown.addEventListener('change', function () {
//      const selectedCountryCode = countryDropdown.value;
//         // console.log(selectedCountryCode);
//      if (selectedCountryCode !== '') {
//          // You can use a different API endpoint for country-specific data
//          // Example: const statesEndpoint = `https://api.example.com/states?country=${selectedCountryCode}`;
//          // Populate states based on the selected country
//          const statesEndpoint = `https://api.example.com/states?country=${selectedCountryCode}`;
//          //console.log(statesEndpoint);
//          populateDropdown(statesEndpoint, 'state');
//      }
// });

// const stateDropdown = document.querySelector("#state");
//  stateDropdown.addEventListener('change', function () {
//      const selectedState = stateDropdown.value;
//         // console.log(selectedState);

//      if (selectedState !== '') {
//          // You can use a different API endpoint for state-specific data
//          // Example: const citiesEndpoint = `https://api.example.com/cities?state=${selectedState}`;
//          // Populate cities based on the selected state
//          const citiesEndpoint = `https://api.example.com/cities?state=${selectedState}`;
//          populateDropdown(citiesEndpoint, 'city');
//      }
// });

personal_next_btn.addEventListener("click", function () {
    const genderMale = document.querySelector("#male");
    const genderFemale = document.querySelector("#female");
    const genderPreferNotSay = document.querySelector("#prefer-not-say");
    if(!(genderMale.checked || genderFemale.checked || genderPreferNotSay.checked))
    {
        alert("Please select your gender.");
        return;
    }
    const day = document.querySelector("#day");
    if(!day.value)
    {
        alert("Please enter your birth-day.");
        return;
    }
    const month = document.querySelector("#month");
    if(!month.value)
    {
        alert("Please enter your birth-month.");
        return;
    }
    const year = document.querySelector("#year");
    if(!year.value)
    {
        alert("Please enter your birth-year.");
        return;
    }
    const countryCodeHome = document.querySelector("#homenumber-postal");
    if (!countryCodeRegex.test(countryCodeHome.value)) {
        alert("Please enter a correct Country Code.");
        return;
    }
    const homeNumber = document.querySelector("#homenumber");
    if (!mobileRegex.test(homeNumber.value)) {
        alert("Please enter a correct mobile number.");
        return;
    }
    const countryCodePhone = document.querySelector("#phonenumber-postal");
    if (!countryCodeRegex.test(countryCodePhone.value)) {
        alert("Please enter a correct Country Code.");
        return;
    }
    const phoneNumber = document.querySelector("#phonenumber");
    if (!mobileRegex.test(phoneNumber.value)) {
        alert("Please enter a correct mobile number.");
        return;
    }
    const postalCode = document.querySelector("#postal-code");
    if (!postalCodeRegex.test(postalCode.value)) {
        alert("Please enter a correct postal code.");
        return;
    }
    var requiredFields = document.querySelectorAll(".required-field-personal");
    var isEmpty = false;
    for (var i = 0; i < requiredFields.length; i++) {
        if (requiredFields[i].value.trim() === "") {
            isEmpty = true;
            console.log("Empty field: ", requiredFields[i]);
            break;
        }
    }

    if (isEmpty) {
        alert("Please fill up all details.");
    } else {
        container.classList.add("education-mode");
        // Initially hide OTP container
        container_personal.style.display = "none";
        container_educational.style.display = "block";
    }
});

educational_next_btn.addEventListener("click", function () {
    const sscPercentage = document.querySelector("#SSC-percentage");
    if (!resultRegex.test(sscPercentage.value)) {
        alert("Please enter correct SSC percentage.");
        return;
    }
    const hscPercentage = document.querySelector("#HSC-percentage");
    if (!resultRegex.test(hscPercentage.value)) {
        alert("Please enter correct HSC percentage.");
        return;
    }
    const gujcetPR = document.querySelector("#GUJCET-percentile-rank");
    if (!resultRegex.test(gujcetPR.value)) {
        alert("Please enter correct GUJCET PR.");
        return;
    }
    const jeeMainPR = document.querySelector("#JEE-main-percentile-rank");
    if (!resultRegex.test(jeeMainPR.value)) {
        alert("Please enter correct JEE-Main PR.");
        return;
    }
    var requiredFieldsEdu = document.querySelectorAll(".required-field");
    var isEmpty = false;

    for (var i = 0; i < requiredFieldsEdu.length; i++) {
        if (requiredFieldsEdu[i].value.trim() === "") {
            isEmpty = true;
            console.log("Empty field: ", requiredFieldsEdu[i]);
            break;
        }
    }

    if (isEmpty) {
        alert("Please fill up all details.");
    } else {
    container.classList.add("payment-mode");
    // Initially hide OTP container
    container_educational.style.display = "none";
    container_payment.style.display = "block";
    }
});

educational_back_btn.addEventListener("click", () => {
    container.classList.add("personal-mode");
    // Initially hide OTP container
    container_educational.style.display = "none";
    container_personal.style.display = "block";
    
});

payment_back_btn.addEventListener("click", () => {
    container.classList.add("educational-mode");
    // Initially hide OTP container
    container_payment.style.display = "none";
    container_educational.style.display = "block";
    
});

payment_submit_btn.addEventListener("click", () =>{
    container.classList.add("sign-in-mode");
    container_payment.style.display = "none";
    container_sign_in.style.display = "block";
});
