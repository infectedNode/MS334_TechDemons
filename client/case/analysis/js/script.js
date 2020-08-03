let map;

// 28.463307, 77.492337
// 28.465278, 77.492230
// 28.463184, 77.489108
// 28.460788, 77.490353
// 28.462194, 77.487306

function updateMap(data){
  map = new google.maps.Map(
    document.getElementById('map'),
    {
      center: new google.maps.LatLng(28.4623779,77.4898183), 
      zoom: 16
    }
  );
  
  let markerImage = new google.maps.MarkerImage(
    'https://cdn0.iconfinder.com/data/icons/electronics-95/64/155-512.png',
    null, /* size is determined at runtime */
    null, /* origin is 0,0 */
    null, /* anchor is bottom center of the scaled image */
    new google.maps.Size(32, 37)
  )

  // Create markers.
  for (let i = 0; i < data.length; i++) {
    let marker = new google.maps.Marker({
      position: {lat: data[i].lat, lng: data[i].long},
      icon: markerImage,
      title: `Camera ID : ${data[i].id} \nFilename : ${data[i].filename} \n(${data[i].lat}, ${data[i].long})`,
      map: map
    });
  };

}

let videoID = null
let record = null

function updateAnalysis(caseID) {
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
          analysis = data.case.analysis;
          videoID = analysis.videoID
          record = analysis.record
          updateMap(videoID)
          updateRecord(record, videoID)
          console.log(analysis)
          $('.loader').removeClass('show')
        } 
      },
      error: function(err) {
          $('.loader').removeClass('show')
          console.log("error" + err);
      }
  });
}

function updateRecord(record, videoID) {
  record.forEach(ele => {
    let vid = ele.vid;
    let filename;
    let link;
    for(let i=0; i<videoID.length; i++){
      if(vid == videoID[i].id){
        filename = videoID[i].filename;
        link = videoID[i].link;
        break;
      }
    }
    ele.detections.forEach(det => {
      $('.search .record .data').append(`
        <div class="rec">
            <div class="vid"><p>${vid}</p></div>
            <div class="filename"><p>${filename}</p></div>
            <div class="date"><p>${det.day}-${det.month}-${det.year}</p></div>
            <div class="time"><p>${det.hour}:${det.minute}</p></div>
            <div class="down"><p><a href="${link}">Click</a></p></div>
        </div>
      `)
    })
    
  });
}

$(document).ready(function(){
  let caseID = localStorage.getItem('caseID');
  if(caseID) {
      updateAnalysis(caseID);
  } else {
      console.log('CaseID not found');
      let url = "/cases";
      window.location.href = url; 
  }
});