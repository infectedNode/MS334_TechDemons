$(document).ready(function(){
    let caseID = localStorage.getItem('caseID');
    if(caseID) {
        // console.log(caseID);
    } else {
        console.log('CaseID not found');
        let url = "/cases";
        window.location.href = url; 
    }
});

function setColor(side, selectedID_list, caseID) {
    $('.loader').addClass('show');
    const URL2 = baseURL + "/setcolor";

    $.ajax({
        url: URL2,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({side, selectedID: selectedID_list}),
        beforeSend: function(request) {
            request.setRequestHeader("caseID", caseID);
        },
        success: (data) => {
            if(data.error){
                $('.loader').removeClass('show');
                console.log(data.error);
            } else {
                if(data.message == "success") {
                    $('.loader').addClass('show');
                    let url = "/case";
                    window.location.href = url; 
                }
                console.log(data);
                $('.loader').removeClass('show');
            }
        },
        error: (err) => {
            $('.loader').removeClass('show')
            console.log(err)
        }
    });
}

function sendTarget(side, file) {
    $('.select').addClass('hide');
    $('.loader').addClass('show');

    const URL = baseURL + `/settarget?side=${side}`;
    let caseID = localStorage.getItem('caseID');

    let fd = new FormData();
    fd.append('image',file);

    $.ajax({
        url: URL,
        type: 'POST',
        data: fd,
        contentType: false,
        processData: false,
        beforeSend: function(request) {
            request.setRequestHeader("caseID", caseID);
        },
        success: function(data){ 
            if(data.error){
                $('.select').removeClass('hide');
                $('.loader').removeClass('show');
                console.log(data.error);
            } else {
                $('.colors').append(`
                    <div class="image">
                        <img src="${baseURL + '/images/' + caseID + '/' + data.side + '.jpg'}" alt="">
                    </div>
                    <div class="info">
                        <p class="side">Side : ${data.side}</p>
                        <p class="feature">Features Found: ${data.features_found}</p>
                    </div>
                `).removeClass('hide');

                let clrs = data.colors;
                $('.select_colors .clrs').append(`
                    <div class="clr" id="${clrs[0].id}" style="background-color: rgb(${clrs[0].rgb[0]},${clrs[0].rgb[1]},${clrs[0].rgb[2]});"></div>
                    <div class="clr" id="${clrs[1].id}" style="background-color: rgb(${clrs[1].rgb[0]},${clrs[1].rgb[1]},${clrs[1].rgb[2]});"></div>
                    <div class="clr" id="${clrs[2].id}" style="background-color: rgb(${clrs[2].rgb[0]},${clrs[2].rgb[1]},${clrs[2].rgb[2]});"></div>
                    <div class="clr" id="${clrs[3].id}" style="background-color: rgb(${clrs[3].rgb[0]},${clrs[3].rgb[1]},${clrs[3].rgb[2]});"></div>
                    <div class="clr" id="${clrs[4].id}" style="background-color: rgb(${clrs[4].rgb[0]},${clrs[4].rgb[1]},${clrs[4].rgb[2]});"></div>
                    <div class="clr" id="${clrs[5].id}" style="background-color: rgb(${clrs[5].rgb[0]},${clrs[5].rgb[1]},${clrs[5].rgb[2]});"></div>
                    <div class="clr" id="${clrs[6].id}" style="background-color: rgb(${clrs[6].rgb[0]},${clrs[6].rgb[1]},${clrs[6].rgb[2]});"></div>
                `)

                $('.select_colors').removeClass('hide');
                $('.loader').removeClass('show');

                selectedIDS = []

                $('.select_colors .clrs .clr').click(function() {
                    $(this).toggleClass('selected');
                    selectedID = parseInt($(this).attr('id'));
                    let found = 0;
                    let i;
                    for(i=0; i<selectedIDS.length; i++) {
                        if(selectedIDS[i] == selectedID){
                            found = 1;
                            break;
                        }
                    }
                    if(found) {
                        selectedIDS.splice(i, 1); 
                    } else {
                        selectedIDS.push(selectedID)
                    }
                });

                $('.select_colors .done').click(function() {
                    if(selectedIDS.length > 0) {
                        setColor(data.side, selectedIDS, caseID);
                    } else {
                        console.log('select color!')
                    }
                });

            }
        },
        error: function(err) {
            $('.select').removeClass('hide');
            $('.loader').removeClass('show')
            console.log("error" + err);
        }
    });
}

$('.select .submit').click(function() {
    selected_side = $('#select_side').val();
    img_file = $('#img_file');

    isValid = 1;

    if(selected_side == '' || img_file[0].files[0] == null) {
        isValid = 0;
        console.log("error in input fields")
    }

    if(isValid) {
        img_file = img_file[0].files[0];
        sendTarget(selected_side, img_file);
    }
    console.log();
});