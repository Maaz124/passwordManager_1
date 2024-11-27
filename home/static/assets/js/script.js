function addFields(val) {
    let value = val.value;
    console.log(value);
    let container = document.getElementById("dynamic_input_field_container"); // Get the element where the inputs will be added to

    // Remove every child it had before
    while (container.hasChildNodes()) {
        container.removeChild(container.lastChild);
    }

    if (value === "Website") {
        let elChild = document.createElement("div");
        elChild.innerHTML = `
                            <div>
                                <div class="form-floating mb-4">
                                    <input type="text" class="form-control" id="website_name" name="website_name"
                                           placeholder="website name">
                                    <label for="website_name">Website name</label>
                                </div>
                                <div class="form-floating mb-4">
                                    <input type="text" class="form-control" id="website_url" name="website_url"
                                           placeholder="url">
                                    <label for="website_url">Website URL</label>
                                </div>
                            </div>`;
        container.appendChild(elChild);
    } else if (value === "Desktop application") {
        let elChild = document.createElement("div");
        elChild.innerHTML = `
                            <div>
                                <div class="form-floating mb-4">
                                    <input type="text" class="form-control" id="application_name" name="application_name"
                                           placeholder="application name">
                                    <label for="application_name">Application name</label>
                                </div>
                            </div>`;
        container.appendChild(elChild);
    } else if (value === "Game") {
        let elChild = document.createElement("div");
        elChild.innerHTML = `
                            <div>
                                <div class="form-floating mb-4">
                                    <input type="text" class="form-control" id="game_name" name="game_name"
                                           placeholder="game name">
                                    <label for="game_name">Game name</label>
                                </div>
                                <div class="form-floating mb-4">
                                    <input type="text" class="form-control" id="game_developer" name="game_developer"
                                           placeholder="game developer">
                                    <label for="game_developer">Game developer</label>
                                </div>
                            </div>`;
        container.appendChild(elChild);
    }
};

function generatePasswordHandler() {
    $.ajax({
        type: 'GET',
        url: '/generate-password/',
        success: function (data) {
            document.getElementsByName('password')[0].value = data.password;
        }
    });
};

function toggleView(id) {
    const input = document.getElementById(id);
    const icon = document.getElementById(`icon-${id}`)
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye")
        icon.classList.add("fa-eye-slash")
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash")
        icon.classList.add("fa-eye")
    }
}
let timerInterval; // Declare the timer interval globally


function useFreeVersion() {
    // Set the initial timer duration (10 minutes)
    const initialTime = 10 * 60;
    
    if (!localStorage.getItem("time_left")) {
        localStorage.setItem("time_left", initialTime); // Save the timer duration in localStorage
    }

    startTimer(); // Start the timer
    document.getElementById("timer").style.display = "inline"; // Show the timer
    closePopup(); // Optionally close the popup
}

function startTimer() {
    const timerElement = document.getElementById("timer");
    let time_left = localStorage.getItem("time_left");

    // Clear any existing interval to avoid multiple timers
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    timerInterval = setInterval(() => {
        time_left--;

        // Update the timer display
        const minutes = Math.floor(time_left / 60);
        const seconds = time_left % 60;
        timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // Save the updated time in localStorage
        localStorage.setItem("time_left", time_left);

        if (time_left <= 0) {
            clearInterval(timerInterval);
            localStorage.removeItem("time_left"); // Clear the saved time
            alert("all of your information will be made public!!!");
            timerElement.style.display = "none"; // Hide the timer after expiry
        }
    }, 1000);
}

// Start the timer automatically if the time is already saved in localStorage
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("time_left")) {
        const time_left = localStorage.getItem("time_left");
        if (time_left > 0) {
            document.getElementById("timer").style.display = "inline"; // Show the timer
            startTimer(); // Resume the timer
        }
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('payment-form');
    const popup = document.getElementById('popup');
    const okButton = document.getElementById('ok-button');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        // Stop the timer
        clearInterval(timerInterval); // Assumes `timerInterval` is globally declared in your timer code
        localStorage.removeItem("time_left"); // Remove saved timer state

        // Collect form data
        const paymentData = {
            cardNumber: document.getElementById('card-number').value,
            expiryDate: document.getElementById('expiry-date').value,
            cvv: document.getElementById('cvv').value,
            cardHolderName: document.getElementById('card-holder-name').value,
        };

        // Send data to the server
        fetch('/process-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}', // Django's CSRF token
            },
            body: JSON.stringify(paymentData),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    popup.classList.remove('hidden'); // Show success popup
                } else {
                    alert('Failed to save payment information. Try again.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred while processing the payment.');
            });
    });

    okButton.addEventListener('click', function () {
        popup.classList.add('hidden'); // Close popup on "OK"
    });
});
