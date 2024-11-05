function register() {
    var formData = new FormData(document.getElementById('registrationForm'));
    var jsonData = {};
    formData.forEach(function(value, key){
        jsonData[key] = value;
    });
    console.log(jsonData)

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data); // Log the response from the server
        alert("If you wish to use this platform, you must contact us to obtain permission.")
        window.open('https://wa.me/5493515119799', '_blank');
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
};
