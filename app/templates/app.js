// Wait for the page to load
document.addEventListener('DOMContentLoaded', () => {

    // 1. Select the elements
    const button = document.getElementById('mainBtn');
    const input = document.getElementById('userInput');
    const feedback = document.getElementById('feedback');

    // 2. Add Click Event
    button.addEventListener('click', () => {
        const inputValue = input.value;

        if (inputValue.trim() === "") {
            // Error state
            alert("Please enter some text first!");
            input.style.borderColor = "red";
        } else {
            // Success state
            input.style.borderColor = "#4E9F3D"; // Green border
            
            // Show feedback message
            feedback.style.display = "block";
            feedback.innerText = "Success! You entered: " + inputValue;
            
            // Console log for debugging
            console.log("User submitted:", inputValue);
        }
    });

});