function updateCases() {
    const URL = baseURL + "/cases"

    $('.loader').addClass('show')

    $.ajax({
        url: URL,
        type: 'GET',
        success: function(data){ 
            if(data.error){
                $('.loader').removeClass('show')
                console.log(data.error);
            } else {

                $('.cases  .case-list').empty();
                cases = data.cases;
                cases.forEach(c => {
                    $('.cases  .case-list').append(`
                        <div class="case" id="${c.caseID}">
                            <div class="name">
                                <p>${c.name}</p>
                            </div>
                            <div class="caseID">
                                <p>${c.caseID}</p>
                            </div>
                        </div>
                    `)
                });

                $('.cases .case-list .case .name p').click(function(){
                    
                    $('.loader').addClass('show')
                    let clickedID = $(this).parent().parent().attr('id');
                            
                    localStorage.setItem("caseID", clickedID);
                        
                    let url = "/case";
                    window.location.href = url; 
                });

                $('.loader').removeClass('show')
            }
        },
        error: function(data) {
            $('.loader').removeClass('show')
            console.log("error");
        }
    });
}

function newCase(name) {
    const URL = baseURL + "/newcase"
    $('.loader').addClass('show');

    $.ajax({
        url: URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({name: name}),
        success: (data) => {
            $('.cases  .case-list').append(`
                <div class="case" id="${data.caseID}">
                    <div class="name">
                        <p>${data.name}</p>
                    </div>
                    <div class="caseID">
                        <p>${data.caseID}</p>
                    </div>
                </div>
            `)

            $(`.cases .case-list .case .name p`).click(function(){
                $('.loader').addClass('show')
                let clickedID = $(this).parent().parent().attr('id');
                localStorage.setItem("caseID", clickedID);     
                let url = "/case";
                window.location.href = url; 
            });

            $('.loader').removeClass('show')
        },
        error: (err) => {
            $('.loader').removeClass('show')
            console.log(err)
        }
    });
}


$(document).ready(function(){
    updateCases();
});


$('.nav .box .refresh').click(function() {
    updateCases();
});


$('.nav .box .new').click(function() {
    $('.addCase').addClass('show');
});

$('.addCase .box .submit').click(function() {
    caseName = $('#case');
    
    isValid = 1
    if(caseName.val() == '' || caseName.val() == null) {
        isValid = 0;
        console.log("provide a name error")
    }

    if(isValid){
        $('.addCase').removeClass('show');
        newCase(caseName.val());
    }
});