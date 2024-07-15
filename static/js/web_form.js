// To automatically generate concise name from the given title
//
// // document.getElementById('title').addEventListener('change', auto_con_name);
// // function auto_con_name(){
// //   var s = document.getElementById('title').value;
// //   document.getElementById('concise_name').value = s;
// // }


document.getElementById('title').addEventListener('change', CheckTitle);
function CheckTitle(val){
  var t = document.getElementById('title').value;
  if (t=='Other'){
    element.style.display='block';
    document.getElementById('new_title').required = true;
  }
  else {
    element.style.display='none';
    document.getElementById('new_title').required = false;
  }
}
