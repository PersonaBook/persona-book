document.addEventListener('DOMContentLoaded', function() {
  var openBtn = document.getElementById('open-chatbot');
  if (openBtn) {
    openBtn.onclick = function(e) {
      e.preventDefault();
      var modal = new bootstrap.Modal(document.getElementById('chatbotModal'));
      modal.show();
    };
  }
  const memoBtn = document.getElementById('open-memo');
  if (memoBtn) {
    memoBtn.onclick = function() {
      alert('메모 기능은 추후 구현 예정입니다.');
    };
  }
});
