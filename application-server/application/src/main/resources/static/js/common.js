// document.addEventListener('DOMContentLoaded', function() {
//   var openBtn = document.getElementById('open-chatbot');
//   if (openBtn) {
//     openBtn.onclick = function(e) {
//       e.preventDefault();
//       var modal = new bootstrap.Modal(document.getElementById('chatbotModal'));
//       modal.show();
//     };
//   }
//   const memoBtn = document.getElementById('open-memo');
//   if (memoBtn) {
//     memoBtn.onclick = function() {
//       alert('메모 기능은 추후 구현 예정입니다.');
//     };
//   }
// });


$(document).ready(function(){
    /* section layout 최소 height */
    function adjustSectionHeight() {
        const vh = $(window).outerHeight();
        const headerH = $('header').outerHeight() || 0;
        $('section').css('min-height', vh - headerH);
        $('section > div').css('min-height', vh - headerH);
        $('section > div > div.container').css('min-height', vh - headerH);
    }

    adjustSectionHeight();

    $(window).on('resize', adjustSectionHeight);
});