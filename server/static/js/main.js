function createAcceptedTable(data, link) {
    const container = document.getElementById('table1');
    // Remove any existing tbody
    var existingTBody = container.querySelector('table tbody');
    if (existingTBody) {
        existingTBody.remove();
        // Create new tbody for the table
        var table = container.querySelector('table');
        var tbody = document.createElement('tbody');

        // Add data to the table
        var row = tbody.insertRow(-1);
        for (var key in data) {
            var cell = row.insertCell(-1);
            if (key === 'bookmaker') {
                var link_betplay_1 = document.createElement('a');
                link_betplay_1.href = link.split("<br>")[0];
                link_betplay_1.target = "_blank"
                link_betplay_1.textContent = data[key].split("<br>")[0];
                cell.appendChild(link_betplay_1);
                cell.appendChild(document.createElement('br'));
                var link_betplay_2 = document.createElement('a');
                link_betplay_2.href = link.split("<br>")[0];
                link_betplay_2.target = "_blank"
                link_betplay_2.textContent = data[key].split("<br>")[1];
                cell.appendChild(link_betplay_2);
                cell.appendChild(document.createElement('br'));
                var link_pinnacle_1 = document.createElement('a');
                link_pinnacle_1.href = link.split("<br>")[1];
                link_pinnacle_1.target = "_blank"
                link_pinnacle_1.textContent = data[key].split("<br>")[2];
                cell.appendChild(link_pinnacle_1);
                cell.appendChild(document.createElement('br'));
                var link_pinnacle_2 = document.createElement('a');
                link_pinnacle_2.href = link.split("<br>")[1];
                link_pinnacle_2.target = "_blank"
                link_pinnacle_2.textContent = data[key].split("<br>")[3];
                cell.appendChild(link_pinnacle_2);

                cell.style.textAlign = 'center';
            } else {
                cell.innerHTML = data[key];
                cell.style.textAlign = 'center';
            }
        }

        // Append the new tbody to the existing table
        table.appendChild(tbody);
    }
    else {
        // Create the table element
        var table = document.createElement('table');

        // Create and append the table header (thead)
        var thead = document.createElement('thead');
        var headerRow = thead.insertRow(0);

        // Create table headers
        for (var key in data) {
            var header = document.createElement('th');
            header.textContent = key.charAt(0).toUpperCase() + key.slice(1);
            header.style.textAlign = 'center';
            headerRow.appendChild(header);
        }

        // Append the <thead> to the table
        table.appendChild(thead);

        // Create and append the table body (tbody)
        var tbody = document.createElement('tbody');

        // Add data to the table body
        var row = tbody.insertRow(-1);
        for (var key in data) {
            var cell = row.insertCell(-1);
            if (key === 'bookmaker') {
                var link_betplay_1 = document.createElement('a');
                link_betplay_1.href = link.split("<br>")[0];
                link_betplay_1.target = "_blank"
                link_betplay_1.textContent = data[key].split("<br>")[0];
                cell.appendChild(link_betplay_1);
                cell.appendChild(document.createElement('br'));
                var link_pinnacle_1 = document.createElement('a');
                link_pinnacle_1.href = link.split("<br>")[1];
                link_pinnacle_1.target = "_blank"
                link_pinnacle_1.textContent = data[key].split("<br>")[2];
                cell.appendChild(link_pinnacle_1);

                cell.style.textAlign = 'center';
            } else {
                cell.innerHTML = data[key];
                cell.style.textAlign = 'center';
            }
        }

        // Append the <tbody> to the table
        table.appendChild(tbody);

        // Display the table on the page
        container.appendChild(table);
    }
}

function createAcceptableTable(dataList, response) {
    const container = document.getElementById('table2');
    // Remove any existing tbody
    var existingTBody = container.querySelector('table tbody');

    if (existingTBody) {
        existingTBody.remove();
        // Create new tbody for the table
        var table = container.querySelector('table');
        var tbody = document.createElement('tbody');

        var accepted = false
        countOfEvents = response.length
        dataList.forEach(function (data, index) {
            var row = tbody.insertRow(-1);
            var temp_data = {}
            var link_format = 'https://betplay.com.co/<br>https://www.pinnacle.com/'
            var button_text = "Accept"
            var button_color = "grey"

            if (index < countOfEvents){
                temp_data = response[index]
                link_format = temp_data["link"]
            }
            for (var key in data) {
                var cell = row.insertCell(-1);
                if (key === 'bookmaker') {
                    var link_betplay_1 = document.createElement('a');
                    link_betplay_1.href = link_format.split("<br>")[0];
                    link_betplay_1.target = "_blank"
                    link_betplay_1.textContent = data[key].split("<br>")[0];
                    cell.appendChild(link_betplay_1);
                    cell.appendChild(document.createElement('br'));
                    var link_betplay_2 = document.createElement('a');
                    link_betplay_2.href = link_format.split("<br>")[0];
                    link_betplay_2.target = "_blank"
                    link_betplay_2.textContent = data[key].split("<br>")[1];
                    cell.appendChild(link_betplay_2);
                    cell.appendChild(document.createElement('br'));
                    var link_pinnacle_1 = document.createElement('a');
                    link_pinnacle_1.href = link_format.split("<br>")[1];
                    link_pinnacle_1.target = "_blank"
                    link_pinnacle_1.textContent = data[key].split("<br>")[2];
                    cell.appendChild(link_pinnacle_1);
                    cell.appendChild(document.createElement('br'));
                    var link_pinnacle_2 = document.createElement('a');
                    link_pinnacle_2.href = link_format.split("<br>")[1];
                    link_pinnacle_2.target = "_blank"
                    link_pinnacle_2.textContent = data[key].split("<br>")[3];
                    cell.appendChild(link_pinnacle_2);

                    cell.style.textAlign = 'center';
                } else {
                    cell.innerHTML = data[key];
                    cell.style.textAlign = 'center';
                }                
            }
            if (options['auto_manual'] == "Auto" && !accepted && data['percent'] >= 1.0 && data['percent'] <= 7.0){
                accept_button_clicked(temp_data, data, link_format)
                accepted = true
                button_text = "Accepted"
                button_color = 'lightblue'
            }
            
            if(data['sports'] != '-'){
                var buttonCell = row.insertCell(-1);
                buttonCell.textContent = button_text;
                buttonCell.style.backgroundColor = button_color;
                buttonCell.style.textAlign = 'center'
                // var button = document.createElement('button');
                // button.textContent = button_text;
                // button.style.border = '1px solid';
                // button.style.borderColor = 'black';
                // button.style.backgroundColor = button_color;
                // button.style.width = '80px'
                // button.style.textAlign = 'center'
                buttonCell.addEventListener('click', function () {
                    if(options['action_mode'] == "Not_using" || (options['action_mode'] != "Not_using" && options['auto_manual'] == "Manual")){
                        accept_button_clicked(temp_data, data, link_format)
                        this.innerText = "Accepted"
                        this.style.backgroundColor = 'lightblue'
                    }
                });
                // buttonCell.appendChild(button);
                buttonCell.style.alignItems = 'center'
            }
            else{
                var cell = row.insertCell(-1);
                cell.innerHTML = '-';
                cell.style.textAlign = 'center';
            }
        });

        // Append the new tbody to the existing table
        table.appendChild(tbody);
    }
    else {
        // Create the table element
        var table = document.createElement('table');

        // Create and append the table header (thead)
        var thead = document.createElement('thead');
        var headerRow = thead.insertRow(0);

        // Create table headers
        for (var key in dataList[0]) {
            var header = document.createElement('th');
            header.textContent = key.charAt(0).toUpperCase() + key.slice(1);
            header.style.textAlign = 'center';
            headerRow.appendChild(header);
        }
        var header = document.createElement('th');
        header.textContent = "Accept";
        header.style.textAlign = 'center';
        headerRow.appendChild(header);

        // Append the <thead> to the table
        table.appendChild(thead);

        // Create and append the table body (tbody)
        var tbody = document.createElement('tbody');

        // Add data to the table body
        dataList.forEach(function (data, index) {
            var row = tbody.insertRow(-1);

            for (var key in data) {
                var cell = row.insertCell(-1);
                if (key === 'bookmaker') {
                    var link_betplay = document.createElement('a');
                    link_betplay.textContent = data[key].split("<br>")[0];
                    cell.appendChild(link_betplay);
                    cell.appendChild(document.createElement('br'));
                    var link_pinnacle = document.createElement('a');
                    link_pinnacle.textContent = data[key].split("<br>")[1];
                    cell.appendChild(link_pinnacle);
                    cell.style.textAlign = 'center';
                } else {
                    cell.innerHTML = data[key];
                    cell.style.textAlign = 'center';
                }
            }
            var cell = row.insertCell(-1);
            cell.innerHTML = '-';
            cell.style.textAlign = 'center';
        });

        // Append the <tbody> to the table
        table.appendChild(tbody);

        // Display the table on the page
        container.appendChild(table);
    }
}

function accept_button_clicked(temp_data, data, link_format) {
    data_format['sports'] = data['sports']
    data_format['percent'] = data['percent']
    data_format['time'] = data['time']
    data_format['bookmaker'] = data['bookmaker']
    data_format['league'] = data['league']
    data_format['eventName'] = data['eventName']
    data_format['period'] = data['period']
    data_format['market'] = data['market']
    data_format['line'] = data['line']
    data_format['odds'] = data['odds']
    
    const currentTime = new Date();
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const seconds = currentTime.getSeconds();
    data_format['at'] = `${hours}:${minutes}:${seconds}`;

    if (options['action_mode'] != 'Not_using'){
        temp_data['action_mode'] = options['action_mode']
        temp_data['auto_manual'] = options['auto_manual']
        fetch('/api/accepted', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(temp_data),
        })
            .then(response => response.json())
            .then(data => {
                if (data["status"] == true) {
                    createAcceptedTable(data_format, link_format)
                    if (options['action_mode'] == "Only_visit" && data["only_visit"] == false) {
                        alert("You're not allowed to use <Only visit>. Please contact us if you wish.")
                    }
                    if (options['action_mode'] == "Full_using" && data["all_options"] == false) {
                        alert("You're not allowed to use <Access to all options>. Please contact us if you wish.")
                    }
                }
                else{
                    if (options['auto_manual'] == "Manual"){
                        alert("It's already running on other event")
                    }
                }
                console.log(data)
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }
    else{
        createAcceptedTable(data_format, link_format)
    }
}

$(document).ready(function () {
    var socket = io();
    socket.on('connect', function () {
        console.log("Conneted to server")
    });

    socket.on('channel_message', function (msg) {
        console.log(msg)
    });
    socket.on('server_to_client', function (response) {
        var dataList = []
        var countOfEvents = response.length
        response.forEach(function (data, index) {
            a = index + 1
            b = data["sports"]
            c = data["percent"]
            d = data["time"]
            e = data["bookmaker"]
            f = data["league"]
            g = data["event"]
            h = data["period"]
            i = data["market"]
            j = data["line"]
            k = data["odds"]
            dataList.push({ no: a, sports: b, percent: c, time: d, bookmaker: e, league: f, eventName: g, period: h, market: i, line: j, odds: k })
        });
        for(let i = countOfEvents; i < 10; i++){
            dataList.push({
                no: '-', sports: '-', percent: '-', time: '-', bookmaker: '-<br>-', league: '-<br>-', eventName: '-<br>-', period: '-<br>-', market: '-<br>-', line: '-<br>-', odds: '-<br>-'
            })
        }
        createAcceptableTable(dataList, response);
    })
});

function selectActionMode() {
    var buttonGroup = document.getElementById("accept_option");
    var optioinFull_using = document.getElementById("full_using");
    var optionOnly_visit= document.getElementById("only_visit");
    var optionNot_using = document.getElementById("not_using");

    if (optioinFull_using.checked) {
        buttonGroup.classList.remove("hidden");
        options['action_mode'] = 'Full_using';
    } 
    else {
        buttonGroup.classList.add("hidden");
        options['auto_manual'] = "Manual";
        if (optionOnly_visit.checked){
            options['action_mode'] = 'Only_visit';
        }
        else{
            options['action_mode'] = 'Not_using';
        }
    }
    console.log(options);
}

function selectAuto_Manual(){
    var optionAuto = document.getElementById("auto_accept");
    if (optionAuto.checked){
        options['auto_manual'] = 'Auto';
    }
    else{
        options['auto_manual'] = 'Manual';
    }
    console.log(options);
}

var options = {action_mode: 'Not_using', auto_manual: 'Manual'};

var dataList_format = [];
for (let i = 0; i < 10; i++) {
    dataList_format.push({
        no: '-', sports: '-', percent: '-', time: '-', bookmaker: '-<br>-<br>-<br>-', league: '-<br>-', eventName: '-<br>-', period: '-<br>-', market: '-<br>-', line: '-<br>-', odds: '-<br>-'
    })
}

var data_format = {
    sports: '-', percent: '-', time: '-', bookmaker: '-<br>-<br>-<br>-', league: '-<br>-', eventName: '-<br>-', period: '-<br>-', market: '-<br>-', line: '-<br>-', odds: '-<br>-', at: '-'
}

var link_format = 'https://betplay.com.co/<br>https://www.pinnacle.com/'

createAcceptedTable(data_format, link_format);
createAcceptableTable(dataList_format, []);
selectActionMode();