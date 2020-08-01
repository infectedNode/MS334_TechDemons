function getColor(colors) {
    clrs = ""
    colors.forEach(color => {
        rgb = color.rgb;
        clrs = clrs + `<div class="c" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]});"></div>`;
    });
    return clrs;
}

function updateCase(caseID) {
    const URL = baseURL + "/case"

    $('.loader').addClass('show');

    $.ajax({
        url: URL,
        type: 'GET',
        beforeSend: function(request) {
            request.setRequestHeader("caseID", caseID);
        },
        success: function(data){ 
            if(data.error){
                $('.loader').removeClass('show')
                console.log(data.error);
            } else {
                let res_case = data.case;
                $('.nav .box .case_name').text(res_case.name);

                $('.main .target .sides').empty();

                if(res_case.target.sides != null) {
                    res_case.target.sides.forEach(side => {
                        $('.main .target .sides').append(`
                            <div class="side">
                                <div class="blck">
                                    <img src="${baseURL + '/images/' + caseID + '/' + side.side + '.jpg'}" alt="">
                                </div>
                                <div class="info">
                                    <p class="name">Side : ${side.side}</p>
                                    <p class="feature">Features : error</p>
                                    <p class="clrs">Colors :- </p>
                                    <div class="colors">
                                        ${getColor(side.colors)}
                                    </div>
                                </div>
                            </div>
                        `)
                    });
                }
                
                $('.loader').removeClass('show')
            }
        },
        error: function(err) {
            $('.loader').removeClass('show')
            console.log("error" + err);
        }
    });
}

let intervalID = 0

function analyse(caseID) {
    const URL = baseURL + "/gettarget"

    $('.main .analysis .view').removeClass('show')
    $('.main .analysis .analyse').addClass('hide')
    $('.main .analysis .load').addClass('show');
    $('.main .analysis .status p').text('starting the process . . .');
    $('.main .analysis .status').addClass('show');

    $.ajax({
        url: URL,
        type: 'POST',
        beforeSend: function(request) {
            request.setRequestHeader("caseID", caseID);
        },
        success: function(data){ 
            if(data.error){
                $('.main .analysis .load').removeClass('show')
                $('.main .analysis .status p').text(data.error);
                $('.main .analysis .analyse').removeClass('hide')
            } else if(data.success){
                $('.main .analysis .status p').text("Status : 0%");
                intervalID = setInterval(getStatus, 5000, caseID);
            }
        },
        error: function(err) {
            $('.main .analysis .load').removeClass('show')
            $('.main .analysis .status p').text('Server is down !');
            $('.main .analysis .analyse').removeClass('hide')
        }
    });
}

function getStatus(caseID) {
    const URL = baseURL + "/getstatus"
    $.ajax({
        url: URL,
        type: 'GET',
        beforeSend: function(request) {
            request.setRequestHeader("caseID", caseID);
        },
        success: function(data){ 
            $('.main .analysis .status p').text(`Status : ${data.status}%`);
            if(data.status == -1 || data.status == 100){
                clearInterval(intervalID);
                $('.main .analysis .load').removeClass('show')
                $('.main .analysis .status p').text("processing complete.");
                $('.main .analysis .analyse').removeClass('hide')
                $('.main .analysis .view').addClass('show')
            }
        },
        error: function(err) {
            clearInterval(intervalID);
            $('.main .analysis .load').removeClass('show')
            $('.main .analysis .status p').text('Server is down !');
            $('.main .analysis .analyse').removeClass('hide')
        }
    });
}

$(document).ready(function(){
    let caseID = localStorage.getItem('caseID');
    if(caseID) {
        updateCase(caseID);
    } else {
        console.log('CaseID not found');
        let url = "/cases";
        window.location.href = url; 
    }
});

$('.nav .box .refresh').click(function() {
    updateCase();
});

$('.main .target .add .add_side').click(function() {
    $('.loader').addClass('show')
    let url = "/case/settarget";
    window.location.href = url; 
});

$('.main .analysis .analyse').click(function() {
    let caseID = localStorage.getItem('caseID');
    if(caseID) {
        analyse(caseID);
    } else {
        console.log('CaseID not found');
        let url = "/cases";
        window.location.href = url; 
    }
});


$('.main .analysis .view').click(function() {
    $('.loader').addClass('show')
    let url = "/case/analysis";
    window.location.href = url; 
});
